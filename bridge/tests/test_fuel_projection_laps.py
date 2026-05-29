from unittest.mock import MagicMock

import pytest

from race_engineer.fuel.projection.laps import normalize_laps_remaining
from race_engineer.fuel.projection.session_laps import SessionLapsReader
from race_engineer.sdk.wrapper import IrSdkWrapper


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (12, 12),
        (0, 0),
        (-1, None),
        (32767, None),
        (None, None),
        ("10", 10),
        ("bad", None),
    ],
)
def test_normalize_laps_remaining(value: object | None, expected: int | None) -> None:
    assert normalize_laps_remaining(value) == expected


def _mock_sdk(var_map: dict[str, object]) -> MagicMock:
    mock = MagicMock(spec=IrSdkWrapper)
    mock.is_connected = True

    def get_var(name: str) -> object:
        return var_map.get(name)

    mock.get_var.side_effect = get_var
    return mock


def test_session_laps_reader() -> None:
    reader = SessionLapsReader(sdk=_mock_sdk({"SessionLapsRemainEx": 8}))

    assert reader.read_laps_remaining() == 8


def test_session_laps_reader_when_disconnected() -> None:
    mock = _mock_sdk({})
    mock.is_connected = False
    reader = SessionLapsReader(sdk=mock)

    assert reader.read_laps_remaining() is None


def test_session_laps_reader_rejects_sentinel() -> None:
    reader = SessionLapsReader(sdk=_mock_sdk({"SessionLapsRemainEx": 32767}))

    assert reader.read_laps_remaining() is None
