from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.api.ws import WebSocketConnectionManager
from race_engineer.connection import SdkConnectionService


@pytest.fixture
def mock_connection_service() -> MagicMock:
    service = MagicMock(spec=SdkConnectionService)
    service.is_connected = False
    service.as_dict.return_value = {
        "state": "disconnected",
        "is_connected": False,
        "sdk_initialized": False,
        "sdk_connected": False,
    }
    return service


@pytest.fixture
def client(mock_connection_service: MagicMock) -> TestClient:
    app = create_app(connection_service=mock_connection_service)
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
