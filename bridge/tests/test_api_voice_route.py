from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.connection import SdkConnectionService


@pytest.fixture
def client() -> TestClient:
    service = MagicMock(spec=SdkConnectionService)
    service.is_connected = False
    service.as_dict.return_value = {
        "state": "disconnected",
        "is_connected": False,
        "sdk_initialized": False,
        "sdk_connected": False,
    }
    service.sdk = MagicMock()
    app = create_app(connection_service=service, voice_pipeline=None)
    with TestClient(app) as test_client:
        yield test_client


def test_route_voice_returns_intent(client: TestClient) -> None:
    response = client.post(
        "/voice/route",
        json={"text": "what is my gap ahead"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["intent"] == "gap"
    assert body["text"] == "what is my gap ahead"
