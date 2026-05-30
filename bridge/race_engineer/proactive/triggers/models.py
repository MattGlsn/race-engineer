from dataclasses import dataclass, field
from enum import StrEnum

from race_engineer.fuel.projection.models import FuelRiskLevel


class TriggerType(StrEnum):
    FASTEST_LAP = "fastest_lap"
    INCIDENT = "incident"
    FUEL = "fuel"
    GAP_CLOSING_AHEAD = "gap_closing_ahead"
    GAP_CLOSING_BEHIND = "gap_closing_behind"


@dataclass(frozen=True, slots=True)
class TriggerSnapshot:
    """Live race inputs for one trigger-engine evaluation."""

    session_key: str | None = None
    player_best_lap_time: float | None = None
    incident_count: int | None = None
    fuel_risk_level: FuelRiskLevel = FuelRiskLevel.UNKNOWN
    gap_ahead_seconds: float | None = None
    gap_behind_seconds: float | None = None


@dataclass(frozen=True, slots=True)
class TriggerEvent:
    type: TriggerType
    payload: dict[str, object] = field(default_factory=dict)
