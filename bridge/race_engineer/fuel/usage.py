import math

MAX_LAP_USAGE_LITERS = 200.0
USAGE_PRECISION = 3


def calculate_lap_usage(
    fuel_start: float | None,
    fuel_end: float | None,
) -> float | None:
    """Return liters consumed on a lap (fuel_start - fuel_end), or None if invalid."""
    if fuel_start is None or fuel_end is None:
        return None

    usage = fuel_start - fuel_end
    if not math.isfinite(usage):
        return None
    if usage < 0 or usage > MAX_LAP_USAGE_LITERS:
        return None

    return round(usage, USAGE_PRECISION)
