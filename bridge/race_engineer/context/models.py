from pydantic import BaseModel, ConfigDict


class SessionContextState(BaseModel):
    """Session metadata for AI engineer context."""

    model_config = ConfigDict(frozen=True)

    track_name: str | None = None
    session_type: str | None = None
    field_size: int = 0


class NearbyStanding(BaseModel):
    """Condensed standing entry near the player."""

    model_config = ConfigDict(frozen=True)

    car_idx: int
    position: int | None = None
    laps: int | None = None


class RaceContextState(BaseModel):
    """Live race picture for AI engineer context."""

    model_config = ConfigDict(frozen=True)

    fuel_level: float | None = None
    overall_position: int | None = None
    class_position: int | None = None
    field_size: int | None = None
    gap_ahead_seconds: float | None = None
    gap_behind_seconds: float | None = None
    fuel_last_lap_usage: float | None = None
    fuel_rolling_avg_usage: float | None = None
    fuel_valid_lap_count: int = 0
    fuel_laps_remaining: int | None = None
    fuel_projected_finish: float | None = None
    fuel_risk_level: str = "unknown"
    fuel_warning: bool = False
    nearby_standings: tuple[NearbyStanding, ...] = ()
