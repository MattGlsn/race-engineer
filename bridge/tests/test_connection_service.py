from unittest.mock import MagicMock

import pytest

from race_engineer.connection import ConnectionState, SdkConnectionService


@pytest.fixture
def mock_sdk() -> MagicMock:
    sdk = MagicMock()
    sdk.is_initialized = False
    sdk.is_connected = False
    sdk.startup.return_value = False
    return sdk


def test_connect_success(mock_sdk: MagicMock) -> None:
    mock_sdk.startup.return_value = True
    mock_sdk.is_initialized = True
    mock_sdk.is_connected = True

    service = SdkConnectionService(sdk=mock_sdk)

    assert service.connect() is True
    assert service.state == ConnectionState.CONNECTED
    assert service.as_dict()["is_connected"] is True
    mock_sdk.startup.assert_called_once()


def test_connect_failure_when_sim_not_running(mock_sdk: MagicMock) -> None:
    service = SdkConnectionService(sdk=mock_sdk)

    assert service.connect() is False
    assert service.state == ConnectionState.DISCONNECTED
    assert service.as_dict()["is_connected"] is False


def test_connect_handles_startup_exception(mock_sdk: MagicMock) -> None:
    mock_sdk.startup.side_effect = RuntimeError("shared memory unavailable")
    service = SdkConnectionService(sdk=mock_sdk)

    assert service.connect() is False
    assert service.state == ConnectionState.DISCONNECTED


def test_disconnect(mock_sdk: MagicMock) -> None:
    mock_sdk.startup.return_value = True
    mock_sdk.is_initialized = True
    mock_sdk.is_connected = True
    service = SdkConnectionService(sdk=mock_sdk)
    service.connect()

    service.disconnect()

    assert service.state == ConnectionState.DISCONNECTED
    mock_sdk.shutdown.assert_called()


def test_disconnect_is_idempotent(mock_sdk: MagicMock) -> None:
    service = SdkConnectionService(sdk=mock_sdk)
    service.disconnect()
    service.disconnect()
    mock_sdk.shutdown.assert_not_called()


def test_check_health_when_connected(mock_sdk: MagicMock) -> None:
    mock_sdk.startup.return_value = True
    mock_sdk.is_initialized = True
    mock_sdk.is_connected = True
    service = SdkConnectionService(sdk=mock_sdk)
    service.connect()

    assert service.check_health() is True
    assert service.state == ConnectionState.CONNECTED


def test_check_health_detects_lost_connection(mock_sdk: MagicMock) -> None:
    mock_sdk.startup.return_value = True
    mock_sdk.is_initialized = True
    mock_sdk.is_connected = True
    service = SdkConnectionService(sdk=mock_sdk)
    service.connect()

    mock_sdk.is_connected = False

    assert service.check_health() is False
    assert service.state == ConnectionState.DISCONNECTED
    mock_sdk.shutdown.assert_called()


def test_reconnect_succeeds_on_second_attempt(
    mock_sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    attempt = {"n": 0}

    def startup() -> bool:
        attempt["n"] += 1
        if attempt["n"] == 1:
            mock_sdk.is_initialized = False
            mock_sdk.is_connected = False
            return False
        mock_sdk.is_initialized = True
        mock_sdk.is_connected = True
        return True

    mock_sdk.startup.side_effect = startup
    monkeypatch.setattr(
        "race_engineer.connection.service.time.sleep",
        lambda _seconds: None,
    )

    service = SdkConnectionService(
        sdk=mock_sdk,
        reconnect_attempts=3,
        reconnect_delay_seconds=0,
    )

    assert service.reconnect() is True
    assert service.state == ConnectionState.CONNECTED
    assert mock_sdk.startup.call_count == 2


def test_reconnect_fails_after_max_attempts(
    mock_sdk: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    mock_sdk.startup.return_value = False
    monkeypatch.setattr(
        "race_engineer.connection.service.time.sleep",
        lambda _seconds: None,
    )

    service = SdkConnectionService(
        sdk=mock_sdk,
        reconnect_attempts=2,
        reconnect_delay_seconds=0,
    )

    assert service.reconnect() is False
    assert service.state == ConnectionState.DISCONNECTED
    assert mock_sdk.startup.call_count == 2
