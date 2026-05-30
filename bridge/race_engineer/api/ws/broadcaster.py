import asyncio
import logging
import time

from race_engineer.api.ws.manager import WebSocketConnectionManager
from race_engineer.api.ws.messages import (
    build_connection_message,
    build_proactive_trigger_message,
    build_race_state_message,
    build_telemetry_message,
)
from race_engineer.proactive.cooldown import CooldownManager
from race_engineer.proactive.incident import IncidentReader
from race_engineer.proactive.suppression import (
    SpeechSuppressionManager,
    WorkloadMonitor,
)
from race_engineer.proactive.lap import PlayerBestLapReader
from race_engineer.proactive.triggers import TriggerEngine, TriggerSnapshot
from race_engineer.coaching.trace import TraceRecorder
from race_engineer.connection import SdkConnectionService
from race_engineer.session import SessionInfoReader
from race_engineer.fuel import (
    FuelConsumptionTracker,
    FuelProjectionEngine,
    PlayerLapReader,
    build_session_key,
)
from race_engineer.fuel.projection import SessionLapsReader
from race_engineer.gap import GapAheadCalculator, GapBehindCalculator
from race_engineer.position import PositionCalculator
from race_engineer.standings import StandingsReader
from race_engineer.telemetry import TelemetryVariableReader
from race_engineer.voice.engineer import EngineerVoiceService

logger = logging.getLogger(__name__)

TELEMETRY_INTERVAL_SECONDS = 0.05
RACE_STATE_INTERVAL_SECONDS = 0.5
SDK_RECONNECT_INTERVAL_SECONDS = 1.0


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
        fuel_projection_engine: FuelProjectionEngine | None = None,
        lap_reader: PlayerLapReader | None = None,
        trace_recorder: TraceRecorder | None = None,
        best_lap_reader: PlayerBestLapReader | None = None,
        incident_reader: IncidentReader | None = None,
        trigger_engine: TriggerEngine | None = None,
        cooldown_manager: CooldownManager | None = None,
        workload_monitor: WorkloadMonitor | None = None,
        suppression_manager: SpeechSuppressionManager | None = None,
        engineer_voice: EngineerVoiceService | None = None,
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
        self._fuel_projection_engine = (
            fuel_projection_engine
            if fuel_projection_engine is not None
            else FuelProjectionEngine(
                session_laps_reader=SessionLapsReader(sdk=connection_service.sdk),
            )
        )
        self._lap_reader = (
            lap_reader
            if lap_reader is not None
            else PlayerLapReader(sdk=connection_service.sdk)
        )
        self._trace_recorder = (
            trace_recorder if trace_recorder is not None else TraceRecorder()
        )
        self._best_lap_reader = (
            best_lap_reader
            if best_lap_reader is not None
            else PlayerBestLapReader(sdk=connection_service.sdk)
        )
        self._incident_reader = (
            incident_reader
            if incident_reader is not None
            else IncidentReader(sdk=connection_service.sdk)
        )
        self._trigger_engine = (
            trigger_engine if trigger_engine is not None else TriggerEngine()
        )
        self._cooldown_manager = (
            cooldown_manager if cooldown_manager is not None else CooldownManager()
        )
        resolved_workload = workload_monitor or WorkloadMonitor()
        self._workload_monitor = resolved_workload
        self._suppression_manager = (
            suppression_manager
            if suppression_manager is not None
            else SpeechSuppressionManager(resolved_workload)
        )
        self._engineer_voice = engineer_voice
        self._telemetry_interval = telemetry_interval
        self._race_state_interval = race_state_interval
        self._task: asyncio.Task[None] | None = None
        self._last_race_state_at = 0.0
        self._last_connection_payload: dict[str, object] | None = None
        self._last_connect_attempt_at = 0.0

    async def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._last_connection_payload = self._connection_service.as_dict()
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

                await self._sync_connection_state()

                snapshot = self._telemetry_reader.read_snapshot()
                telemetry_now = time.monotonic()
                self._workload_monitor.observe(snapshot, now=telemetry_now)
                if self._engineer_voice is not None:
                    await asyncio.to_thread(self._engineer_voice.flush_pending_speech)
                laps_completed = self._lap_reader.read_laps_completed()
                fuel_snapshot = self._fuel_tracker.update(
                    snapshot.fuel,
                    laps_completed,
                )
                self._trace_recorder.record(snapshot, laps_completed)
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
                            self._trace_recorder.begin_session(session_key)
                            self._cooldown_manager.begin_session(session_key)
                            self._workload_monitor.reset()
                            self._suppression_manager.reset()
                            fuel_snapshot = self._fuel_tracker.update(
                                snapshot.fuel,
                                laps_completed,
                            )
                        standings = self._standings_reader.read_snapshot()
                        player_position = self._position_calculator.calculate()
                        gap_ahead = self._gap_calculator.calculate()
                        gap_behind = self._gap_behind_calculator.calculate()
                        fuel_projection = self._fuel_projection_engine.project(
                            snapshot.fuel,
                            fuel_snapshot,
                        )
                        await self._manager.broadcast(
                            build_race_state_message(
                                session,
                                standings,
                                player_position,
                                gap_ahead,
                                gap_behind,
                                fuel_snapshot,
                                fuel_projection,
                            ),
                        )
                        trigger_snapshot = TriggerSnapshot(
                            session_key=session_key,
                            player_best_lap_time=self._best_lap_reader.read_best_lap_time(),
                            incident_count=self._incident_reader.read_incident_count(),
                            fuel_risk_level=fuel_projection.risk_level,
                            gap_ahead_seconds=gap_ahead.gap_seconds,
                            gap_behind_seconds=gap_behind.gap_seconds,
                        )
                        trigger_events = self._trigger_engine.evaluate(trigger_snapshot)
                        for trigger_event in self._cooldown_manager.filter(
                            trigger_events,
                        ):
                            for released in self._suppression_manager.accept_trigger(
                                trigger_event,
                                now=now,
                            ):
                                await self._manager.broadcast(
                                    build_proactive_trigger_message(released),
                                )
                        for released in self._suppression_manager.drain_triggers(
                            now=now,
                        ):
                            await self._manager.broadcast(
                                build_proactive_trigger_message(released),
                            )

                await asyncio.sleep(self._telemetry_interval)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Telemetry broadcaster failed")
            raise

    async def _sync_connection_state(self) -> None:
        if self._connection_service.is_connected:
            self._connection_service.check_health()
        else:
            now = time.monotonic()
            if now - self._last_connect_attempt_at >= SDK_RECONNECT_INTERVAL_SECONDS:
                self._last_connect_attempt_at = now
                self._connection_service.connect()

        connection_payload = self._connection_service.as_dict()
        if connection_payload != self._last_connection_payload:
            self._last_connection_payload = connection_payload
            await self._manager.broadcast(build_connection_message(connection_payload))
