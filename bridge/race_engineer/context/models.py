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


class DriverContextState(BaseModel):
    """Player identity and standing stats for AI engineer context."""

    model_config = ConfigDict(frozen=True)

    car_idx: int | None = None
    user_name: str | None = None
    car_number: str | None = None
    car_class: str | None = None
    laps_completed: int | None = None
    best_lap_time: float | None = None


class LapFuelSummary(BaseModel):
    """Condensed per-lap fuel usage for analytics context."""

    model_config = ConfigDict(frozen=True)

    lap: int
    usage_liters: float


class AnalyticsContextState(BaseModel):
    """Aggregated fuel and lap analytics for AI engineer context."""

    model_config = ConfigDict(frozen=True)

    valid_lap_count: int = 0
    rolling_avg_usage: float | None = None
    last_lap_usage: float | None = None
    recent_lap_fuel: tuple[LapFuelSummary, ...] = ()


class EngineerContext(BaseModel):
    """Root schema for AI engineer race context."""

    model_config = ConfigDict(frozen=True)

    session: SessionContextState
    race: RaceContextState
    driver: DriverContextState
    analytics: AnalyticsContextState
