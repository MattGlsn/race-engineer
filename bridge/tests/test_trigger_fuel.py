from race_engineer.fuel.projection.models import FuelRiskLevel
from race_engineer.proactive.triggers.fuel import evaluate_fuel
from race_engineer.proactive.triggers.models import TriggerSnapshot, TriggerType


def test_fuel_fires_when_entering_caution() -> None:
    snapshot = TriggerSnapshot(fuel_risk_level=FuelRiskLevel.CAUTION)

    event, last_risk = evaluate_fuel(
        snapshot,
        last_risk_level=FuelRiskLevel.SAFE,
    )

    assert event is not None
    assert event.type == TriggerType.FUEL
    assert event.payload["risk_level"] == "caution"
    assert last_risk == FuelRiskLevel.CAUTION


def test_fuel_does_not_repeat_while_warning_active() -> None:
    snapshot = TriggerSnapshot(fuel_risk_level=FuelRiskLevel.CRITICAL)

    event, last_risk = evaluate_fuel(
        snapshot,
        last_risk_level=FuelRiskLevel.CAUTION,
    )

    assert event is None
    assert last_risk == FuelRiskLevel.CRITICAL


def test_fuel_resets_when_returning_to_safe() -> None:
    snapshot = TriggerSnapshot(fuel_risk_level=FuelRiskLevel.SAFE)

    event, last_risk = evaluate_fuel(
        snapshot,
        last_risk_level=FuelRiskLevel.CRITICAL,
    )

    assert event is None
    assert last_risk == FuelRiskLevel.SAFE


def test_fuel_fires_again_after_safe_reset() -> None:
    snapshot = TriggerSnapshot(fuel_risk_level=FuelRiskLevel.CAUTION)

    event, _ = evaluate_fuel(
        snapshot,
        last_risk_level=FuelRiskLevel.SAFE,
    )

    assert event is not None
