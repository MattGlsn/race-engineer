from race_engineer.fuel.projection.models import FuelRiskLevel


def classify_fuel_risk(
    projected_finish_fuel: float | None,
    avg_usage_per_lap: float | None,
) -> FuelRiskLevel:
    """Classify fuel risk from projected finish fuel."""
    if projected_finish_fuel is None:
        return FuelRiskLevel.UNKNOWN

    if projected_finish_fuel <= 0:
        return FuelRiskLevel.CRITICAL

    if avg_usage_per_lap is not None and projected_finish_fuel < avg_usage_per_lap:
        return FuelRiskLevel.CAUTION

    return FuelRiskLevel.SAFE


def fuel_warning_active(risk_level: FuelRiskLevel) -> bool:
    return risk_level in (FuelRiskLevel.CAUTION, FuelRiskLevel.CRITICAL)
