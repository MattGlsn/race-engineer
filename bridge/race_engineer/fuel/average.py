DEFAULT_ROLLING_WINDOW = 5
USAGE_PRECISION = 3


def rolling_average(
    usages: list[float],
    window: int = DEFAULT_ROLLING_WINDOW,
) -> float | None:
    """Return the mean usage over the most recent valid laps."""
    if not usages or window <= 0:
        return None

    sample = usages[-window:]
    return round(sum(sample) / len(sample), USAGE_PRECISION)
