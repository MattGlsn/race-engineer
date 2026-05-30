from race_engineer.fuel.projection.models import FuelRiskLevel
from race_engineer.proactive.triggers.models import TriggerEvent, TriggerType


def trigger_priority(event: TriggerEvent) -> int:
    """Lower values are higher priority."""
    if event.type == TriggerType.INCIDENT:
        return 0
    if event.type == TriggerType.FUEL:
        if event.payload.get("risk_level") == FuelRiskLevel.CRITICAL.value:
            return 1
        return 2
    if event.type == TriggerType.GAP_CLOSING_AHEAD:
        return 3
    if event.type == TriggerType.GAP_CLOSING_BEHIND:
        return 4
    if event.type == TriggerType.FASTEST_LAP:
        return 5
    return 6


def bypasses_global_throttle(event: TriggerEvent) -> bool:
    if event.type == TriggerType.INCIDENT:
        return True
    if event.type == TriggerType.FUEL:
        return event.payload.get("risk_level") == FuelRiskLevel.CRITICAL.value
    return False


def sort_by_priority(events: tuple[TriggerEvent, ...]) -> tuple[TriggerEvent, ...]:
    return tuple(sorted(events, key=trigger_priority))
