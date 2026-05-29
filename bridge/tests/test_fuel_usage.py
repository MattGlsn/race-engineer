import pytest

from race_engineer.fuel.usage import calculate_lap_usage


@pytest.mark.parametrize(
    ("fuel_start", "fuel_end", "expected"),
    [
        (30.0, 28.5, 1.5),
        (10.0, 10.0, 0.0),
        (None, 5.0, None),
        (5.0, None, None),
        (5.0, 6.0, None),
        (5.0, float("nan"), None),
        (201.0, 0.0, None),
    ],
)
def test_calculate_lap_usage(
    fuel_start: float | None,
    fuel_end: float | None,
    expected: float | None,
) -> None:
    assert calculate_lap_usage(fuel_start, fuel_end) == expected
