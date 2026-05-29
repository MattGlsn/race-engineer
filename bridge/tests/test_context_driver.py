from race_engineer.context.driver import build_driver_state
from race_engineer.context.models import DriverContextState
from race_engineer.position.models import PlayerPositionSnapshot
from race_engineer.session.models import Driver, Session
from race_engineer.standings.models import DriverStanding, StandingsSnapshot


def test_build_driver_state() -> None:
    session = Session(
        track_name="Spa-Francorchamps",
        session_type="Race",
        drivers=(
            Driver(
                car_idx=1,
                user_name="Player",
                car_number="42",
                car_class_short_name="GT3",
            ),
        ),
    )
    standings = StandingsSnapshot(
        drivers=(
            DriverStanding(
                car_idx=1,
                position=2,
                laps=8,
                best_lap_time=142.321,
            ),
        ),
    )
    player = PlayerPositionSnapshot(car_idx=1, overall_position=2)

    state = build_driver_state(session, standings, player)

    assert state == DriverContextState(
        car_idx=1,
        user_name="Player",
        car_number="42",
        car_class="GT3",
        laps_completed=8,
        best_lap_time=142.321,
    )


def test_build_driver_state_without_player() -> None:
    state = build_driver_state(
        Session(),
        StandingsSnapshot(),
        PlayerPositionSnapshot(),
    )

    assert state == DriverContextState()
