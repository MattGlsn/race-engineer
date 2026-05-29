from unittest.mock import MagicMock

import pytest

from race_engineer.gap import GapBehindCalculator, GapBehindSnapshot


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
    calculator = GapBehindCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == GapBehindSnapshot()
    mock_sdk.freeze_var_buffer_latest.assert_not_called()


def test_calculate_gap_seconds_from_distance_and_speed(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(
        mock_sdk,
        {
            "CarDistBehind": 25.0,
            "Speed": 50.0,
        },
    )
    calculator = GapBehindCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == GapBehindSnapshot(
        gap_seconds=0.5,
        distance_meters=25.0,
    )


def test_zero_speed_returns_no_gap_seconds(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(
        mock_sdk,
        {
            "CarDistBehind": 10.0,
            "Speed": 0.0,
        },
    )
    calculator = GapBehindCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == GapBehindSnapshot(distance_meters=10.0)
