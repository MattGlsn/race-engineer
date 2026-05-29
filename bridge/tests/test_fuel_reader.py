from unittest.mock import MagicMock

from race_engineer.fuel.reader import PlayerLapReader
from race_engineer.sdk.wrapper import IrSdkWrapper


def _mock_sdk(var_map: dict[str, object]) -> MagicMock:
    mock = MagicMock(spec=IrSdkWrapper)
    mock.is_connected = True

    def get_var(name: str) -> object:
        return var_map.get(name)

    mock.get_var.side_effect = get_var
    return mock


def test_read_laps_completed() -> None:
    reader = PlayerLapReader(
        sdk=_mock_sdk(
            {
                "PlayerCarIdx": 2,
                "CarIdxLapCompleted": [0, 0, 5, 0],
            },
        ),
    )

    assert reader.read_laps_completed() == 5


def test_read_laps_completed_when_disconnected() -> None:
    mock = _mock_sdk({})
    mock.is_connected = False
    reader = PlayerLapReader(sdk=mock)

    assert reader.read_laps_completed() is None
