from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.ai.prompt.models import PersonalityMode
from race_engineer.api.app import create_app
from race_engineer.connection import SdkConnectionService
from race_engineer.settings.personality import PersonalitySettings


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
def personality_settings() -> PersonalitySettings:
    return PersonalitySettings(PersonalityMode.DIRECT)


@pytest.fixture
def client(
    mock_connection_service: MagicMock,
    personality_settings: PersonalitySettings,
) -> TestClient:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        voice_pipeline=None,
        personality_settings=personality_settings,
    )
    with TestClient(app) as test_client:
        yield test_client


def test_get_personality_defaults_to_direct(
    client: TestClient,
) -> None:
    response = client.get("/settings/personality")

    assert response.status_code == 200
    assert response.json() == {"mode": "direct"}


def test_update_personality(
    client: TestClient,
    personality_settings: PersonalitySettings,
) -> None:
    response = client.put(
        "/settings/personality",
        json={"mode": "intense"},
    )

    assert response.status_code == 200
    assert response.json() == {"mode": "intense"}
    assert personality_settings.mode == PersonalityMode.INTENSE

    get_response = client.get("/settings/personality")
    assert get_response.json() == {"mode": "intense"}


def test_update_personality_rejects_invalid_mode(client: TestClient) -> None:
    response = client.put(
        "/settings/personality",
        json={"mode": "loud"},
    )

    assert response.status_code == 422
