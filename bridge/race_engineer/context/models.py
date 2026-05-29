from pydantic import BaseModel, ConfigDict


class SessionContextState(BaseModel):
    """Session metadata for AI engineer context."""

    model_config = ConfigDict(frozen=True)

    track_name: str | None = None
    session_type: str | None = None
    field_size: int = 0
