from unittest.mock import MagicMock

import pytest

from race_engineer.gap import GapAheadCalculator, GapAheadSnapshot


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
    calculator = GapAheadCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == GapAheadSnapshot()
    mock_sdk.freeze_var_buffer_latest.assert_not_called()


def test_leader_has_no_target_car(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[2] = 1
    lap_completed = [0] * 64
    lap_completed[2] = 10
    lap_dist_pct = [0.0] * 64
    lap_dist_pct[2] = 0.5
    _var_map(
        mock_sdk,
        {
            "PlayerCarIdx": 2,
            "CarIdxPosition": positions,
            "CarIdxLapCompleted": lap_completed,
            "CarIdxLapDistPct": lap_dist_pct,
        },
    )
    calculator = GapAheadCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == GapAheadSnapshot()


def test_find_target_by_track_position_same_lap(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[4] = 3
    positions[7] = 2
    lap_completed = [0] * 64
    lap_completed[4] = 10
    lap_completed[7] = 10
    lap_dist_pct = [0.0] * 64
    lap_dist_pct[4] = 0.40
    lap_dist_pct[7] = 0.55
    _var_map(
        mock_sdk,
        {
            "PlayerCarIdx": 4,
            "CarIdxPosition": positions,
            "CarIdxLapCompleted": lap_completed,
            "CarIdxLapDistPct": lap_dist_pct,
        },
    )
    calculator = GapAheadCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == GapAheadSnapshot(target_car_idx=7)


def test_multiclass_uses_track_position_not_classification(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[4] = 5
    positions[1] = 1
    positions[9] = 4
    lap_completed = [0] * 64
    lap_completed[4] = 10
    lap_completed[1] = 10
    lap_completed[9] = 10
    lap_dist_pct = [0.0] * 64
    lap_dist_pct[4] = 0.50
    lap_dist_pct[1] = 0.90
    lap_dist_pct[9] = 0.52
    _var_map(
        mock_sdk,
        {
            "PlayerCarIdx": 4,
            "CarIdxPosition": positions,
            "CarIdxLapCompleted": lap_completed,
            "CarIdxLapDistPct": lap_dist_pct,
        },
    )
    calculator = GapAheadCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot.target_car_idx == 9


def test_classification_fallback_when_track_data_missing(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[3] = 3
    positions[8] = 2
    _var_map(
        mock_sdk,
        {
            "PlayerCarIdx": 3,
            "CarIdxPosition": positions,
        },
    )
    calculator = GapAheadCalculator(sdk=mock_sdk)

    snapshot = calculator.calculate()

    assert snapshot == GapAheadSnapshot(target_car_idx=8)
