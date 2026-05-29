import pytest

from race_engineer.fuel.projection.finish import calculate_finish_fuel


@pytest.mark.parametrize(
    ("fuel_level", "laps_remaining", "avg_usage", "expected"),
    [
        (30.0, 10, 1.5, 15.0),
        (25.0, 5, 2.0, 15.0),
        (20.0, 0, 1.5, 20.0),
        (None, 5, 1.5, None),
        (20.0, None, 1.5, None),
        (20.0, 5, None, None),
    ],
)
def test_calculate_finish_fuel(
    fuel_level: float | None,
    laps_remaining: int | None,
    avg_usage: float | None,
    expected: float | None,
) -> None:
    assert calculate_finish_fuel(fuel_level, laps_remaining, avg_usage) == expected


def test_finish_fuel_projection_within_five_percent() -> None:
    """DoD: projection error <5% for known inputs."""
    actual_finish = 12.4
    fuel_level = 30.0
    laps_remaining = 10
    avg_usage = (fuel_level - actual_finish) / laps_remaining

    projected = calculate_finish_fuel(fuel_level, laps_remaining, avg_usage)
    assert projected is not None

    error_pct = abs(projected - actual_finish) / actual_finish * 100
    assert error_pct < 5.0
