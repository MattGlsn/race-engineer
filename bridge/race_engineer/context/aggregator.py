from race_engineer.connection import SdkConnectionService
from race_engineer.context.analytics import build_analytics_state
from race_engineer.context.driver import build_driver_state
from race_engineer.context.models import (
    AnalyticsContextState,
    DriverContextState,
    EngineerContext,
    RaceContextState,
    SessionContextState,
)
from race_engineer.context.race import build_race_state
from race_engineer.context.session import build_session_state
from race_engineer.context.validation import validate_engineer_context
from race_engineer.fuel import (
    FuelConsumptionTracker,
    FuelProjectionEngine,
    PlayerLapReader,
    build_session_key,
)
from race_engineer.fuel.projection import SessionLapsReader
from race_engineer.gap import GapAheadCalculator, GapBehindCalculator
from race_engineer.position import PositionCalculator
from race_engineer.session import SessionInfoReader
from race_engineer.standings import StandingsReader
from race_engineer.storage.fuel_repository import FuelLapRepository
from race_engineer.telemetry import TelemetryVariableReader


def empty_engineer_context() -> EngineerContext:
    """Return an empty, schema-valid engineer context."""
    return EngineerContext(
        session=SessionContextState(),
        race=RaceContextState(),
        driver=DriverContextState(),
        analytics=AnalyticsContextState(),
    )


class ContextAggregator:
    """Build compact, validated AI engineer context from live SDK snapshots."""

    def __init__(
        self,
        connection_service: SdkConnectionService,
        *,
        session_reader: SessionInfoReader | None = None,
        standings_reader: StandingsReader | None = None,
        position_calculator: PositionCalculator | None = None,
        gap_ahead_calculator: GapAheadCalculator | None = None,
        gap_behind_calculator: GapBehindCalculator | None = None,
        telemetry_reader: TelemetryVariableReader | None = None,
        fuel_tracker: FuelConsumptionTracker | None = None,
        fuel_projection_engine: FuelProjectionEngine | None = None,
        lap_reader: PlayerLapReader | None = None,
        fuel_repository: FuelLapRepository | None = None,
    ) -> None:
        sdk = connection_service.sdk
        self._connection_service = connection_service
        self._session_reader = session_reader or SessionInfoReader(sdk=sdk)
        self._standings_reader = standings_reader or StandingsReader(sdk=sdk)
        self._position_calculator = position_calculator or PositionCalculator(sdk=sdk)
        self._gap_ahead_calculator = (
            gap_ahead_calculator or GapAheadCalculator(sdk=sdk)
        )
        self._gap_behind_calculator = (
            gap_behind_calculator or GapBehindCalculator(sdk=sdk)
        )
        self._telemetry_reader = telemetry_reader or TelemetryVariableReader(sdk=sdk)
        self._fuel_tracker = fuel_tracker or FuelConsumptionTracker()
        self._fuel_projection_engine = fuel_projection_engine or FuelProjectionEngine(
            session_laps_reader=SessionLapsReader(sdk=sdk),
        )
        self._lap_reader = lap_reader or PlayerLapReader(sdk=sdk)
        self._fuel_repository = fuel_repository

    def build(self) -> EngineerContext:
        """Read live SDK state and return validated engineer context."""
        if not self._connection_service.is_connected:
            context = empty_engineer_context()
            validate_engineer_context(context)
            return context

        session = self._session_reader.read()
        session_key = build_session_key(session.track_name, session.session_type)
        if session_key != self._fuel_tracker.session_key:
            self._fuel_tracker.begin_session(session_key)

        telemetry = self._telemetry_reader.read_snapshot()
        laps_completed = self._lap_reader.read_laps_completed()
        fuel_consumption = self._fuel_tracker.update(telemetry.fuel, laps_completed)
        standings = self._standings_reader.read_snapshot()
        player_position = self._position_calculator.calculate()
        gap_ahead = self._gap_ahead_calculator.calculate()
        gap_behind = self._gap_behind_calculator.calculate()
        fuel_projection = self._fuel_projection_engine.project(
            telemetry.fuel,
            fuel_consumption,
        )

        context = EngineerContext(
            session=build_session_state(session),
            race=build_race_state(
                standings=standings,
                player_position=player_position,
                gap_ahead=gap_ahead,
                gap_behind=gap_behind,
                fuel_level=telemetry.fuel,
                fuel_consumption=fuel_consumption,
                fuel_projection=fuel_projection,
            ),
            driver=build_driver_state(session, standings, player_position),
            analytics=build_analytics_state(
                fuel_consumption,
                repository=self._fuel_repository,
                session_key=session_key,
            ),
        )
        validate_engineer_context(context)
        return context

    def build_payload(self) -> str:
        """Build engineer context and return validated JSON payload."""
        return validate_engineer_context(self.build())
