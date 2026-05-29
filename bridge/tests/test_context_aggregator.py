import pytest

from race_engineer.context.aggregator import ContextAggregator, empty_engineer_context
from race_engineer.context.models import EngineerContext, SessionContextState
from race_engineer.context.validation import (
    MAX_CONTEXT_BYTES,
    assert_no_raw_telemetry,
    validate_context_size,
    validate_engineer_context,
)
from race_engineer.fuel.models import FuelConsumptionSnapshot
from race_engineer.fuel.projection.models import FuelProjectionSnapshot, FuelRiskLevel
from race_engineer.gap.models import GapAheadSnapshot, GapBehindSnapshot
from race_engineer.position.models import PlayerPositionSnapshot
from race_engineer.session.models import Driver, Session
from race_engineer.standings.models import DriverStanding, StandingsSnapshot


class FakeConnectionService:
    def __init__(self, *, connected: bool) -> None:
        self.is_connected = connected
        self.sdk = None


class FakeSessionReader:
    def __init__(self, session: Session) -> None:
        self._session = session

    def read(self) -> Session:
        return self._session


class FakeStandingsReader:
    def __init__(self, standings: StandingsSnapshot) -> None:
        self._standings = standings

    def read_snapshot(self) -> StandingsSnapshot:
        return self._standings


class FakePositionCalculator:
    def __init__(self, snapshot: PlayerPositionSnapshot) -> None:
        self._snapshot = snapshot

    def calculate(self) -> PlayerPositionSnapshot:
        return self._snapshot


class FakeGapAheadCalculator:
    def calculate(self) -> GapAheadSnapshot:
        return GapAheadSnapshot(target_car_idx=0, gap_seconds=1.1)


class FakeGapBehindCalculator:
    def calculate(self) -> GapBehindSnapshot:
        return GapBehindSnapshot(target_car_idx=2, gap_seconds=0.7)


class FakeTelemetryReader:
    def read_snapshot(self):
        from race_engineer.telemetry.models import TelemetrySnapshot

        return TelemetrySnapshot(fuel=40.0)


class FakeLapReader:
    def read_laps_completed(self) -> int:
        return 5


class FakeFuelProjectionEngine:
    def project(self, fuel_level, fuel_consumption):
        return FuelProjectionSnapshot(
            laps_remaining=10,
            projected_finish_fuel=20.0,
            risk_level=FuelRiskLevel.SAFE,
        )


class FakeFuelTracker:
    session_key = "Spa-Francorchamps|Race"

    def begin_session(self, session_key: str) -> None:
        self.session_key = session_key

    def update(self, fuel_level, laps_completed):
        return FuelConsumptionSnapshot(
            last_lap_usage=2.0,
            rolling_avg_usage=2.0,
            valid_lap_count=5,
        )


def test_empty_engineer_context_is_valid() -> None:
    payload = validate_engineer_context(empty_engineer_context())

    assert payload.startswith("{")
    assert len(payload.encode("utf-8")) < MAX_CONTEXT_BYTES


def test_assert_no_raw_telemetry_rejects_forbidden_keys() -> None:
    with pytest.raises(ValueError, match="throttle"):
        assert_no_raw_telemetry({"race": {"throttle": 1.0}})


def test_validate_context_size_rejects_large_payload() -> None:
    with pytest.raises(ValueError, match="exceeds"):
        validate_context_size("x" * (MAX_CONTEXT_BYTES + 1))


def test_context_aggregator_builds_connected_context() -> None:
    session = Session(
        track_name="Spa-Francorchamps",
        session_type="Race",
        drivers=(Driver(car_idx=1, user_name="Player", car_number="42"),),
    )
    standings = StandingsSnapshot(
        drivers=(DriverStanding(car_idx=1, position=2, laps=5, best_lap_time=142.0),),
    )
    aggregator = ContextAggregator(
        FakeConnectionService(connected=True),
        session_reader=FakeSessionReader(session),
        standings_reader=FakeStandingsReader(standings),
        position_calculator=FakePositionCalculator(
            PlayerPositionSnapshot(car_idx=1, overall_position=2, field_size=1),
        ),
        gap_ahead_calculator=FakeGapAheadCalculator(),
        gap_behind_calculator=FakeGapBehindCalculator(),
        telemetry_reader=FakeTelemetryReader(),
        fuel_tracker=FakeFuelTracker(),
        fuel_projection_engine=FakeFuelProjectionEngine(),
        lap_reader=FakeLapReader(),
    )

    context = aggregator.build()
    payload = aggregator.build_payload()

    assert isinstance(context, EngineerContext)
    assert context.session == SessionContextState(
        track_name="Spa-Francorchamps",
        session_type="Race",
        field_size=1,
    )
    assert context.driver.user_name == "Player"
    assert context.race.fuel_level == 40.0
    assert "throttle" not in payload
    assert len(payload.encode("utf-8")) < MAX_CONTEXT_BYTES


def test_context_aggregator_returns_empty_context_when_disconnected() -> None:
    aggregator = ContextAggregator(FakeConnectionService(connected=False))

    context = aggregator.build()

    assert context == empty_engineer_context()
