from race_engineer.fuel.average import rolling_average


def test_rolling_average_empty() -> None:
    assert rolling_average([]) is None


def test_rolling_average_uses_recent_window() -> None:
    assert rolling_average([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], window=3) == 5.0


def test_rolling_average_all_samples_when_fewer_than_window() -> None:
    assert rolling_average([2.0, 4.0], window=5) == 3.0
