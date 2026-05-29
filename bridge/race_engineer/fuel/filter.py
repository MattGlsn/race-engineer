import statistics

SPIKE_RATIO = 2.5
MIN_SAMPLES_FOR_SPIKE = 2


def is_spike(usage: float, recent_valid_usages: list[float]) -> bool:
    """Return True when a lap usage looks like bad telemetry or a pit stop."""
    if usage <= 0:
        return True
    if len(recent_valid_usages) < MIN_SAMPLES_FOR_SPIKE:
        return False

    median = statistics.median(recent_valid_usages)
    if median <= 0:
        return False

    return usage > SPIKE_RATIO * median
