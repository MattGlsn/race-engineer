from race_engineer.position import (
    PlayerPositionSnapshot,
    count_active_positions,
    empty_snapshot,
    normalize_car_idx,
    normalize_positive_int,
)


def test_normalize_positive_int() -> None:
    assert normalize_positive_int(1) == 1
    assert normalize_positive_int(12) == 12
    assert normalize_positive_int(0) is None
    assert normalize_positive_int(-1) is None
    assert normalize_positive_int("3") == 3
    assert normalize_positive_int("bad") is None


def test_normalize_car_idx() -> None:
    assert normalize_car_idx(0) == 0
    assert normalize_car_idx(63) == 63
    assert normalize_car_idx(-1) is None
    assert normalize_car_idx(64) is None
    assert normalize_car_idx("2") == 2
    assert normalize_car_idx(None) is None


def test_count_active_positions() -> None:
    positions = [0] * 64
    positions[0] = 1
    positions[5] = 2
    positions[9] = 3

    assert count_active_positions(positions) == 3
    assert count_active_positions(None) is None


def test_empty_snapshot() -> None:
    assert empty_snapshot() == PlayerPositionSnapshot()
