import time
from unittest.mock import MagicMock

import pytest

from race_engineer.telemetry import TelemetrySnapshot, TelemetryVariableReader
from race_engineer.telemetry.validation import is_valid_snapshot, validate_snapshot


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
    def getitem(key: str) -> object:
        if key not in values:
            raise KeyError(key)
        return values[key]

    mock_sdk.__getitem__.side_effect = getitem
    mock_sdk.get_var.side_effect = lambda name: values.get(name)


def test_read_snapshot_disconnected_returns_nulls(mock_sdk: MagicMock) -> None:
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot == TelemetrySnapshot()
    mock_sdk.freeze_var_buffer_latest.assert_not_called()


def test_read_speed(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"Speed": 42.5})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.speed == 42.5
    mock_sdk.freeze_var_buffer_latest.assert_called_once()
    mock_sdk.unfreeze_var_buffer_latest.assert_called_once()


def test_read_fuel(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"FuelLevel": 28.0})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.fuel == 28.0


def test_read_lap_dist_pct(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"LapDistPct": 0.42})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.lap_dist_pct == 0.42


def test_read_gear(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"Gear": 3})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.gear == 3


def test_read_throttle(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"Throttle": 0.75})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.throttle == 0.75


def test_read_brake(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"Brake": 0.5})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.brake == 0.5


def test_read_steering(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"SteeringWheelAngle": -0.12})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.steering == -0.12


def test_read_rpm(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"RPM": 6500.0})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.rpm == 6500.0


def test_read_snapshot_all_variables(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(
        mock_sdk,
        {
            "Speed": 55.0,
            "FuelLevel": 30.0,
            "LapDistPct": 0.5,
            "Gear": 4,
            "Throttle": 1.0,
            "Brake": 0.0,
            "SteeringWheelAngle": 0.1,
            "RPM": 8000.0,
        },
    )
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot == TelemetrySnapshot(
        speed=55.0,
        fuel=30.0,
        lap_dist_pct=0.5,
        gear=4,
        throttle=1.0,
        brake=0.0,
        steering=0.1,
        rpm=8000.0,
    )
    assert is_valid_snapshot(snapshot)


def test_missing_variable_returns_none(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"Speed": 10.0})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.speed == 10.0
    assert snapshot.rpm is None


def test_invalid_numeric_value_returns_none(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"Speed": "not-a-number"})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.speed is None


def test_unfreeze_called_on_read_error(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    mock_sdk.__getitem__.side_effect = RuntimeError("buffer error")
    mock_sdk.get_var.side_effect = RuntimeError("buffer error")
    reader = TelemetryVariableReader(sdk=mock_sdk)

    snapshot = reader.read_snapshot()

    assert snapshot.speed is None
    mock_sdk.unfreeze_var_buffer_latest.assert_called_once()


def test_read_snapshot_supports_over_20hz(mock_sdk: MagicMock) -> None:
    _connected_sdk(mock_sdk)
    _var_map(mock_sdk, {"Speed": 1.0, "RPM": 1000.0})
    reader = TelemetryVariableReader(sdk=mock_sdk)

    start = time.perf_counter()
    for _ in range(25):
        reader.read_snapshot()
    elapsed = time.perf_counter() - start

    assert elapsed < 1.0


def test_validate_snapshot_rejects_out_of_range() -> None:
    snapshot = TelemetrySnapshot(speed=-1.0, throttle=2.0)

    errors = validate_snapshot(snapshot)

    assert "speed out of range" in errors[0]
    assert "throttle out of range" in errors[1]
    assert is_valid_snapshot(TelemetrySnapshot(speed=10.0, throttle=0.5))
