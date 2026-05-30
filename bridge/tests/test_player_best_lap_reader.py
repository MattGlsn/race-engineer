from unittest.mock import MagicMock

import pytest

from race_engineer.proactive.lap.reader import PlayerBestLapReader
from race_engineer.sdk.wrapper import IrSdkWrapper


def _mock_sdk(var_map: dict[str, object]) -> MagicMock:
    mock = MagicMock(spec=IrSdkWrapper)
    mock.is_connected = True

    def get_var(name: str) -> object:
        return var_map.get(name)

    mock.get_var.side_effect = get_var
    return mock


def test_player_best_lap_reader() -> None:
    reader = PlayerBestLapReader(
        sdk=_mock_sdk(
            {
                "PlayerCarIdx": 2,
                "CarIdxBestLapTime": [0.0, 0.0, 91.234, 0.0],
            },
        ),
    )

    assert reader.read_best_lap_time() == pytest.approx(91.234)


def test_player_best_lap_reader_returns_none_when_unset() -> None:
    reader = PlayerBestLapReader(
        sdk=_mock_sdk(
            {
                "PlayerCarIdx": 1,
                "CarIdxBestLapTime": [0.0, 0.0, 0.0],
            },
        ),
    )

    assert reader.read_best_lap_time() is None
