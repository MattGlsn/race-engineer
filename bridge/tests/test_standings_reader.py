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
        DriverStanding(car_idx=3, position=1, laps=None, class_position=None, class_id=None),
        DriverStanding(car_idx=0, position=2, laps=None, class_position=None, class_id=None),
        DriverStanding(car_idx=7, position=3, laps=None, class_position=None, class_id=None),
    )
    mock_sdk.freeze_var_buffer_latest.assert_called_once()
    mock_sdk.unfreeze_var_buffer_latest.assert_called_once()


def test_missing_position_array_returns_empty(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {})
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot == StandingsSnapshot()


def test_read_lap_counts(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[0] = 1
    positions[5] = 2
    laps = [0] * 64
    laps[0] = 12
    laps[5] = 11
    _var_map(
        mock_sdk,
        {
            "CarIdxPosition": positions,
            "CarIdxLapCompleted": laps,
        },
    )
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.drivers == (
        DriverStanding(car_idx=0, position=1, laps=12, class_position=None, class_id=None),
        DriverStanding(car_idx=5, position=2, laps=11, class_position=None, class_id=None),
    )


def test_missing_lap_array_returns_none_laps(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[2] = 1
    _var_map(mock_sdk, {"CarIdxPosition": positions})
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.drivers == (
        DriverStanding(
            car_idx=2,
            position=1,
            laps=None,
            class_position=None,
            class_id=None,
        ),
    )


def test_read_class_positions_multiclass(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[1] = 2
    positions[4] = 1
    positions[9] = 3
    class_positions = [0] * 64
    class_positions[1] = 1
    class_positions[4] = 1
    class_positions[9] = 2
    class_ids = [0] * 64
    class_ids[1] = 0
    class_ids[4] = 1
    class_ids[9] = 1
    _var_map(
        mock_sdk,
        {
            "CarIdxPosition": positions,
            "CarIdxClassPosition": class_positions,
            "CarIdxClass": class_ids,
        },
    )
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.drivers == (
        DriverStanding(
            car_idx=4,
            position=1,
            laps=None,
            class_position=1,
            class_id=1,
        ),
        DriverStanding(
            car_idx=1,
            position=2,
            laps=None,
            class_position=1,
            class_id=0,
        ),
        DriverStanding(
            car_idx=9,
            position=3,
            laps=None,
            class_position=2,
            class_id=1,
        ),
    )


def test_read_best_lap_times(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[0] = 1
    positions[8] = 2
    best_laps = [0.0] * 64
    best_laps[0] = 87.512
    best_laps[8] = 88.004
    _var_map(
        mock_sdk,
        {
            "CarIdxPosition": positions,
            "CarIdxBestLapTime": best_laps,
        },
    )
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.drivers == (
        DriverStanding(car_idx=0, position=1, best_lap_time=87.512),
        DriverStanding(car_idx=8, position=2, best_lap_time=88.004),
    )


def test_invalid_best_lap_time_returns_none(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    positions = [0] * 64
    positions[3] = 1
    best_laps = [0.0] * 64
    best_laps[3] = -1.0
    _var_map(
        mock_sdk,
        {
            "CarIdxPosition": positions,
            "CarIdxBestLapTime": best_laps,
        },
    )
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.drivers == (
        DriverStanding(car_idx=3, position=1, best_lap_time=None),
    )


def test_unfreeze_called_on_read_error(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    mock_sdk.get_var.side_effect = RuntimeError("buffer error")
    reader = StandingsReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot == StandingsSnapshot()
    mock_sdk.unfreeze_var_buffer_latest.assert_called_once()
