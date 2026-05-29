from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.api.ws import TelemetryBroadcaster, WebSocketConnectionManager
from race_engineer.connection import SdkConnectionService
from race_engineer.telemetry import TelemetrySnapshot


@pytest.fixture
def mock_connection_service() -> MagicMock:
    service = MagicMock(spec=SdkConnectionService)
    service.is_connected = False
    service.sdk = MagicMock()
    service.as_dict.return_value = {
        "state": "disconnected",
        "is_connected": False,
        "sdk_initialized": False,
        "sdk_connected": False,
    }
    return service


@pytest.fixture
def mock_telemetry_reader() -> MagicMock:
    reader = MagicMock()
    reader.read_snapshot.return_value = TelemetrySnapshot(
        speed=42.0,
        rpm=6000.0,
        gear=3,
    )
    return reader


@pytest.fixture
def ws_manager() -> WebSocketConnectionManager:
    return WebSocketConnectionManager()


@pytest.fixture
def broadcaster(
    ws_manager: WebSocketConnectionManager,
    mock_connection_service: MagicMock,
    mock_telemetry_reader: MagicMock,
) -> TelemetryBroadcaster:
    return TelemetryBroadcaster(
        ws_manager,
        mock_connection_service,
        telemetry_reader=mock_telemetry_reader,
        session_reader=MagicMock(),
        standings_reader=MagicMock(),
        telemetry_interval=0.01,
        race_state_interval=None,
    )


@pytest.fixture
def client(
    mock_connection_service: MagicMock,
    ws_manager: WebSocketConnectionManager,
    broadcaster: TelemetryBroadcaster,
) -> TestClient:
    app = create_app(
        connection_service=mock_connection_service,
        ws_manager=ws_manager,
        broadcaster=broadcaster,
    )
    with TestClient(app) as test_client:
        yield test_client


def test_websocket_sends_connection_message(
    client: TestClient,
    mock_connection_service: MagicMock,
) -> None:
    with client.websocket_connect("/ws") as websocket:
        message = websocket.receive_json()

    assert message["type"] == "connection"
    assert message["data"] == mock_connection_service.as_dict.return_value
    assert "ts" in message


def test_websocket_broadcasts_telemetry(
    client: TestClient,
    mock_telemetry_reader: MagicMock,
) -> None:
    with client.websocket_connect("/ws") as websocket:
        websocket.receive_json()
        telemetry = websocket.receive_json()

    assert telemetry["type"] == "telemetry"
    assert telemetry["data"]["speed"] == 42.0
    assert telemetry["data"]["rpm"] == 6000.0
    assert telemetry["data"]["gear"] == 3
    mock_telemetry_reader.read_snapshot.assert_called()


def test_websocket_disconnect_removes_client(
    client: TestClient,
    ws_manager: WebSocketConnectionManager,
) -> None:
    with client.websocket_connect("/ws") as websocket:
        assert ws_manager.client_count == 1
        websocket.receive_json()

    assert ws_manager.client_count == 0


def test_multiple_websocket_clients_receive_broadcast(
    client: TestClient,
) -> None:
    with (
        client.websocket_connect("/ws") as first,
        client.websocket_connect("/ws") as second,
    ):
        first.receive_json()
        second.receive_json()
        first_telemetry = first.receive_json()
        second_telemetry = second.receive_json()

    assert first_telemetry["type"] == "telemetry"
    assert second_telemetry["type"] == "telemetry"
    assert first_telemetry["data"]["speed"] == second_telemetry["data"]["speed"]
