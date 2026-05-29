"""Laps remaining helpers for fuel projection."""

INVALID_LAPS_REMAIN_SENTINEL = 32767


def normalize_laps_remaining(value: object | None) -> int | None:
    """Return validated laps remaining, or None when unavailable."""
    if value is None:
        return None

    try:
        laps = int(value)
    except (TypeError, ValueError):
        return None

    if laps < 0 or laps >= INVALID_LAPS_REMAIN_SENTINEL:
        return None

    return laps
