from race_engineer.fuel.projection.models import FuelRiskLevel
from race_engineer.proactive.triggers.models import TriggerEvent, TriggerSnapshot, TriggerType

_WARNING_LEVELS = frozenset({FuelRiskLevel.CAUTION, FuelRiskLevel.CRITICAL})


def evaluate_fuel(
    snapshot: TriggerSnapshot,
    *,
    last_risk_level: FuelRiskLevel,
) -> tuple[TriggerEvent | None, FuelRiskLevel]:
    """Return a fuel trigger when risk enters warning territory."""
    risk_level = snapshot.fuel_risk_level

    if risk_level not in _WARNING_LEVELS:
        return None, risk_level

    if last_risk_level in _WARNING_LEVELS:
        return None, risk_level

    return (
        TriggerEvent(
            type=TriggerType.FUEL,
            payload={"risk_level": risk_level.value},
        ),
        risk_level,
    )
