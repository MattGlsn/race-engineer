from unittest.mock import MagicMock

import pytest

from race_engineer.position import PlayerPositionSnapshot, PositionCalculator


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


def test_calculate_disconnected_returns_empty(mock_sdk: MagicMock) -> None:
    calculator = PositionCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == PlayerPositionSnapshot()
    mock_sdk.freeze_var_buffer_latest.assert_not_called()


def test_read_player_overall_position(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[3] = 2
    positions[7] = 1
    _var_map(
        mock_sdk,
        {
            "PlayerCarIdx": 3,
            "CarIdxPosition": positions,
        },
    )
    calculator = PositionCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == PlayerPositionSnapshot(
        car_idx=3,
        overall_position=2,
        class_position=None,
        field_size=2,
    )
    mock_sdk.freeze_var_buffer_latest.assert_called_once()
    mock_sdk.unfreeze_var_buffer_latest.assert_called_once()


def test_missing_player_car_idx_returns_empty(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[0] = 1
    _var_map(mock_sdk, {"CarIdxPosition": positions})
    calculator = PositionCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == PlayerPositionSnapshot()


def test_invalid_player_position_returns_none(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[5] = 0
    _var_map(
        mock_sdk,
        {
            "PlayerCarIdx": 5,
            "CarIdxPosition": positions,
        },
    )
    calculator = PositionCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == PlayerPositionSnapshot(
        car_idx=5,
        overall_position=None,
        class_position=None,
        field_size=0,
    )
