from race_engineer.context.models import NearbyStanding, RaceContextState
from race_engineer.context.race import build_race_state
from race_engineer.fuel.models import FuelConsumptionSnapshot
from race_engineer.fuel.projection.models import FuelProjectionSnapshot, FuelRiskLevel
from race_engineer.gap.models import GapAheadSnapshot, GapBehindSnapshot
from race_engineer.position.models import PlayerPositionSnapshot
from race_engineer.standings.models import DriverStanding, StandingsSnapshot


def test_build_race_state() -> None:
    standings = StandingsSnapshot(
        drivers=(
            DriverStanding(car_idx=0, position=1, laps=10),
            DriverStanding(car_idx=1, position=2, laps=10),
            DriverStanding(car_idx=2, position=3, laps=9),
        ),
    )
    player = PlayerPositionSnapshot(
        car_idx=1,
        overall_position=2,
        class_position=2,
        field_size=3,
    )

    state = build_race_state(
        standings=standings,
        player_position=player,
        gap_ahead=GapAheadSnapshot(target_car_idx=0, gap_seconds=1.2),
        gap_behind=GapBehindSnapshot(target_car_idx=2, gap_seconds=0.8),
        fuel_level=42.5,
        fuel_consumption=FuelConsumptionSnapshot(
            last_lap_usage=2.1,
            rolling_avg_usage=2.0,
            valid_lap_count=5,
        ),
        fuel_projection=FuelProjectionSnapshot(
            laps_remaining=12,
            projected_finish_fuel=18.0,
            risk_level=FuelRiskLevel.SAFE,
            warning=False,
        ),
    )

    assert state == RaceContextState(
        fuel_level=42.5,
        overall_position=2,
        class_position=2,
        field_size=3,
        gap_ahead_seconds=1.2,
        gap_behind_seconds=0.8,
        fuel_last_lap_usage=2.1,
        fuel_rolling_avg_usage=2.0,
        fuel_valid_lap_count=5,
        fuel_laps_remaining=12,
        fuel_projected_finish=18.0,
        fuel_risk_level="safe",
        fuel_warning=False,
        nearby_standings=(
            NearbyStanding(car_idx=0, position=1, laps=10),
            NearbyStanding(car_idx=1, position=2, laps=10),
            NearbyStanding(car_idx=2, position=3, laps=9),
        ),
    )


def test_build_race_state_without_player() -> None:
    state = build_race_state(
        standings=StandingsSnapshot(),
        player_position=PlayerPositionSnapshot(),
    )

    assert state.nearby_standings == ()
    assert state.overall_position is None
