FUEL_PRECISION = 3


def calculate_finish_fuel(
    fuel_level: float | None,
    laps_remaining: int | None,
    avg_usage_per_lap: float | None,
) -> float | None:
    """Project liters of fuel at session end."""
    if fuel_level is None or laps_remaining is None or avg_usage_per_lap is None:
        return None

    if laps_remaining < 0 or avg_usage_per_lap < 0:
        return None

    projected = fuel_level - (laps_remaining * avg_usage_per_lap)
    return round(projected, FUEL_PRECISION)
