import asyncio
import logging
import time

from race_engineer.api.ws.manager import WebSocketConnectionManager
from race_engineer.api.ws.messages import build_race_state_message, build_telemetry_message
from race_engineer.connection import SdkConnectionService
from race_engineer.session import SessionInfoReader
from race_engineer.position import PositionCalculator
from race_engineer.standings import StandingsReader
from race_engineer.telemetry import TelemetryVariableReader

logger = logging.getLogger(__name__)

TELEMETRY_INTERVAL_SECONDS = 0.05
RACE_STATE_INTERVAL_SECONDS = 0.5


class TelemetryBroadcaster:
    """Polls the SDK and broadcasts telemetry and race state to WebSocket clients."""

    def __init__(
        self,
        manager: WebSocketConnectionManager,
        connection_service: SdkConnectionService,
        telemetry_reader: TelemetryVariableReader | None = None,
        session_reader: SessionInfoReader | None = None,
        standings_reader: StandingsReader | None = None,
        position_calculator: PositionCalculator | None = None,
        telemetry_interval: float = TELEMETRY_INTERVAL_SECONDS,
        race_state_interval: float | None = RACE_STATE_INTERVAL_SECONDS,
    ) -> None:
        self._manager = manager
        self._connection_service = connection_service
        self._telemetry_reader = (
            telemetry_reader
            if telemetry_reader is not None
            else TelemetryVariableReader(sdk=connection_service.sdk)
        )
        self._session_reader = (
            session_reader
            if session_reader is not None
            else SessionInfoReader(sdk=connection_service.sdk)
        )
        self._standings_reader = (
            standings_reader
            if standings_reader is not None
            else StandingsReader(sdk=connection_service.sdk)
        )
        self._position_calculator = (
            position_calculator
            if position_calculator is not None
            else PositionCalculator(sdk=connection_service.sdk)
        )
        self._telemetry_interval = telemetry_interval
        self._race_state_interval = race_state_interval
        self._task: asyncio.Task[None] | None = None
        self._last_race_state_at = 0.0

    async def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._task = asyncio.create_task(self._run(), name="telemetry-broadcaster")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None

    async def _run(self) -> None:
        try:
            while True:
                if not self._manager.has_clients():
                    await asyncio.sleep(self._telemetry_interval)
                    continue

                if self._connection_service.is_connected:
                    self._connection_service.check_health()

                snapshot = self._telemetry_reader.read_snapshot()
                await self._manager.broadcast(build_telemetry_message(snapshot))

                if self._race_state_interval is not None:
                    now = time.monotonic()
                    if now - self._last_race_state_at >= self._race_state_interval:
                        self._last_race_state_at = now
                        session = self._session_reader.read()
                        standings = self._standings_reader.read_snapshot()
                        player_position = self._position_calculator.calculate()
                        await self._manager.broadcast(
                            build_race_state_message(
                                session,
                                standings,
                                player_position,
                            ),
                        )

                await asyncio.sleep(self._telemetry_interval)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Telemetry broadcaster failed")
            raise
