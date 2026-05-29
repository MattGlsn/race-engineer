from race_engineer.context import SessionContextState, build_session_state
from race_engineer.session.models import Driver, Session


def test_build_session_state() -> None:
    session = Session(
        track_name="Spa-Francorchamps",
        session_type="Race",
        drivers=(
            Driver(car_idx=0, user_name="Player", car_number="42"),
            Driver(car_idx=1, user_name="Rival", car_number="7"),
        ),
    )

    state = build_session_state(session)

    assert state == SessionContextState(
        track_name="Spa-Francorchamps",
        session_type="Race",
        field_size=2,
    )


def test_build_session_state_empty_session() -> None:
    state = build_session_state(Session())

    assert state.track_name is None
    assert state.session_type is None
    assert state.field_size == 0
