import asyncio
import logging
import time

from race_engineer.api.ws.manager import WebSocketConnectionManager
from race_engineer.api.ws.messages import build_race_state_message, build_telemetry_message
from race_engineer.connection import SdkConnectionService
from race_engineer.session import SessionInfoReader
from race_engineer.fuel import FuelConsumptionTracker, PlayerLapReader, build_session_key
from race_engineer.gap import GapAheadCalculator, GapBehindCalculator
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
        gap_calculator: GapAheadCalculator | None = None,
        gap_behind_calculator: GapBehindCalculator | None = None,
        fuel_tracker: FuelConsumptionTracker | None = None,
        lap_reader: PlayerLapReader | None = None,
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
        self._gap_calculator = (
            gap_calculator
            if gap_calculator is not None
            else GapAheadCalculator(sdk=connection_service.sdk)
        )
        self._gap_behind_calculator = (
            gap_behind_calculator
            if gap_behind_calculator is not None
            else GapBehindCalculator(sdk=connection_service.sdk)
        )
        self._fuel_tracker = (
            fuel_tracker if fuel_tracker is not None else FuelConsumptionTracker()
        )
        self._lap_reader = (
            lap_reader
            if lap_reader is not None
            else PlayerLapReader(sdk=connection_service.sdk)
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
                laps_completed = self._lap_reader.read_laps_completed()
                fuel_snapshot = self._fuel_tracker.update(
                    snapshot.fuel,
                    laps_completed,
                )
                await self._manager.broadcast(build_telemetry_message(snapshot))

                if self._race_state_interval is not None:
                    now = time.monotonic()
                    if now - self._last_race_state_at >= self._race_state_interval:
                        self._last_race_state_at = now
                        session = self._session_reader.read()
                        session_key = build_session_key(
                            session.track_name,
                            session.session_type,
                        )
                        if session_key != self._fuel_tracker.session_key:
                            self._fuel_tracker.begin_session(session_key)
                            fuel_snapshot = self._fuel_tracker.update(
                                snapshot.fuel,
                                laps_completed,
                            )
                        standings = self._standings_reader.read_snapshot()
                        player_position = self._position_calculator.calculate()
                        gap_ahead = self._gap_calculator.calculate()
                        gap_behind = self._gap_behind_calculator.calculate()
                        await self._manager.broadcast(
                            build_race_state_message(
                                session,
                                standings,
                                player_position,
                                gap_ahead,
                                gap_behind,
                                fuel_snapshot,
                            ),
                        )

                await asyncio.sleep(self._telemetry_interval)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Telemetry broadcaster failed")
            raise
