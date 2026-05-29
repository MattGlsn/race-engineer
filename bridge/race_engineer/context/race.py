from race_engineer.context.models import NearbyStanding, RaceContextState
from race_engineer.fuel.models import FuelConsumptionSnapshot
from race_engineer.fuel.projection.models import FuelProjectionSnapshot
from race_engineer.gap.models import GapAheadSnapshot, GapBehindSnapshot
from race_engineer.position.models import PlayerPositionSnapshot
from race_engineer.standings.models import DriverStanding, StandingsSnapshot

NEARBY_STANDINGS_WINDOW = 2


def build_race_state(
    *,
    standings: StandingsSnapshot,
    player_position: PlayerPositionSnapshot,
    gap_ahead: GapAheadSnapshot | None = None,
    gap_behind: GapBehindSnapshot | None = None,
    fuel_level: float | None = None,
    fuel_consumption: FuelConsumptionSnapshot | None = None,
    fuel_projection: FuelProjectionSnapshot | None = None,
) -> RaceContextState:
    """Build compact live race context from aggregated SDK snapshots."""
    consumption = fuel_consumption or FuelConsumptionSnapshot()
    projection = fuel_projection or FuelProjectionSnapshot()
    ahead = gap_ahead or GapAheadSnapshot()
    behind = gap_behind or GapBehindSnapshot()

    return RaceContextState(
        fuel_level=fuel_level,
        overall_position=player_position.overall_position,
        class_position=player_position.class_position,
        field_size=player_position.field_size,
        gap_ahead_seconds=ahead.gap_seconds,
        gap_behind_seconds=behind.gap_seconds,
        fuel_last_lap_usage=consumption.last_lap_usage,
        fuel_rolling_avg_usage=consumption.rolling_avg_usage,
        fuel_valid_lap_count=consumption.valid_lap_count,
        fuel_laps_remaining=projection.laps_remaining,
        fuel_projected_finish=projection.projected_finish_fuel,
        fuel_risk_level=projection.risk_level.value,
        fuel_warning=projection.warning,
        nearby_standings=_select_nearby_standings(
            standings.drivers,
            player_position.car_idx,
        ),
    )


def _select_nearby_standings(
    drivers: tuple[DriverStanding, ...],
    player_car_idx: int | None,
    window: int = NEARBY_STANDINGS_WINDOW,
) -> tuple[NearbyStanding, ...]:
    if player_car_idx is None or not drivers:
        return ()

    ordered = sorted(
        drivers,
        key=lambda driver: driver.position if driver.position is not None else 9999,
    )
    player_index = next(
        (index for index, driver in enumerate(ordered) if driver.car_idx == player_car_idx),
        None,
    )
    if player_index is None:
        return ()

    start = max(0, player_index - window)
    end = min(len(ordered), player_index + window + 1)
    return tuple(
        NearbyStanding(
            car_idx=driver.car_idx,
            position=driver.position,
            laps=driver.laps,
        )
        for driver in ordered[start:end]
    )
