from unittest.mock import MagicMock

import pytest

from race_engineer.standings import DriverStanding, StandingsReader, StandingsSnapshot


@pytest.fixture
def mock_sdk() -> MagicMock:
    sdk = MagicMock()
    sdk.is_initialized = False
    sdk.is_connected = False
    return sdk


def _connected_sdk(mock_sdk: MagicMock) -> None:
    mock_sdk.is_initialized = True
    mock_sdk.is_connected = True


def _var_map(mock_sdk: MagicMock, values: dict[str, object]) -> None:
    mock_sdk.get_var.side_effect = lambda name: values.get(name)


def test_read_snapshot_disconnected_returns_empty(mock_sdk: MagicMock) -> None:
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot == StandingsSnapshot()
    mock_sdk.freeze_var_buffer_latest.assert_not_called()


def test_read_positions(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[0] = 2
    positions[3] = 1
    positions[7] = 3
    _var_map(mock_sdk, {"CarIdxPosition": positions})
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.drivers == (
        DriverStanding(car_idx=3, position=1),
        DriverStanding(car_idx=0, position=2),
        DriverStanding(car_idx=7, position=3),
    )
    mock_sdk.freeze_var_buffer_latest.assert_called_once()
    mock_sdk.unfreeze_var_buffer_latest.assert_called_once()


def test_missing_position_array_returns_empty(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {})
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot == StandingsSnapshot()


def test_unfreeze_called_on_read_error(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    mock_sdk.get_var.side_effect = RuntimeError("buffer error")
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot == StandingsSnapshot()
    mock_sdk.unfreeze_var_buffer_latest.assert_called_once()
