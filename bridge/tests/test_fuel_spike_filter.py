import pytest

from race_engineer.fuel.filter import is_spike


@pytest.mark.parametrize(
    ("usage", "recent", "expected"),
    [
        (0.0, [1.5, 1.6], True),
        (-1.0, [1.5], True),
        (1.5, [], False),
        (1.5, [1.4], False),
        (4.0, [1.5, 1.6, 1.4], True),
        (3.5, [1.5, 1.6, 1.4], False),
    ],
)
def test_is_spike(usage: float, recent: list[float], expected: bool) -> None:
    assert is_spike(usage, recent) is expected
