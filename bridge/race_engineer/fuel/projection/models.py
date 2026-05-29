from dataclasses import dataclass
from enum import StrEnum


class FuelRiskLevel(StrEnum):
    """Fuel sufficiency risk based on projected finish fuel."""

    SAFE = "safe"
    CAUTION = "caution"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class FuelProjectionSnapshot:
    """Forward-looking fuel projection for the current session."""

    laps_remaining: int | None = None
    projected_finish_fuel: float | None = None
    risk_level: FuelRiskLevel = FuelRiskLevel.UNKNOWN
    warning: bool = False
