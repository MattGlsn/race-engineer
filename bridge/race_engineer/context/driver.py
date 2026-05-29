from race_engineer.context.models import DriverContextState
from race_engineer.position.models import PlayerPositionSnapshot
from race_engineer.session.models import Session
from race_engineer.standings.models import StandingsSnapshot


def build_driver_state(
    session: Session,
    standings: StandingsSnapshot,
    player_position: PlayerPositionSnapshot,
) -> DriverContextState:
    """Build player identity and standing stats from session and standings data."""
    car_idx = player_position.car_idx
    if car_idx is None:
        return DriverContextState()

    driver = next(
        (entry for entry in session.drivers if entry.car_idx == car_idx),
        None,
    )
    standing = next(
        (entry for entry in standings.drivers if entry.car_idx == car_idx),
        None,
    )

    return DriverContextState(
        car_idx=car_idx,
        user_name=driver.user_name if driver is not None else None,
        car_number=driver.car_number if driver is not None else None,
        car_class=driver.car_class_short_name if driver is not None else None,
        laps_completed=standing.laps if standing is not None else None,
        best_lap_time=standing.best_lap_time if standing is not None else None,
    )
