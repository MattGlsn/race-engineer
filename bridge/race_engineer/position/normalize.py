from race_engineer.position.models import PlayerPositionSnapshot

MAX_CARS = 64


def normalize_positive_int(value: object) -> int | None:
    """Map SDK integers to a 1-based position, or None when unset/invalid."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None

    return parsed if parsed > 0 else None


def normalize_car_idx(value: object) -> int | None:
    """Map PlayerCarIdx to a valid car index, or None when unset/invalid."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None

    if parsed < 0 or parsed >= MAX_CARS:
        return None

    return parsed


def count_active_positions(positions: list[int] | None) -> int | None:
    """Count cars with a valid overall position in the standings array."""
    if positions is None:
        return None

    return sum(1 for position in positions[:MAX_CARS] if position > 0)


def empty_snapshot() -> PlayerPositionSnapshot:
    """Return an empty snapshot for disconnected or unavailable SDK data."""
    return PlayerPositionSnapshot()
