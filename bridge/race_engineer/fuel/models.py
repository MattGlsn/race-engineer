from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LapFuelRecord:
    """Fuel readings for one completed lap."""

    lap: int
    fuel_start: float
    fuel_end: float
    usage_liters: float


@dataclass(frozen=True, slots=True)
class FuelConsumptionSnapshot:
    """Live fuel consumption metrics for the current session."""

    last_lap: int | None = None
    last_lap_usage: float | None = None
    rolling_avg_usage: float | None = None
    valid_lap_count: int = 0
    fuel_at_lap_start: float | None = None
