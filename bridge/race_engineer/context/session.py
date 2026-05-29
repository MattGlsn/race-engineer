from race_engineer.context.models import SessionContextState
from race_engineer.session.models import Session


def build_session_state(session: Session) -> SessionContextState:
    """Build compact session metadata from parsed iRacing session info."""
    return SessionContextState(
        track_name=session.track_name,
        session_type=session.session_type,
        field_size=len(session.drivers),
    )
