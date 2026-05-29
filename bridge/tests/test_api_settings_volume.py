from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.connection import SdkConnectionService
from race_engineer.settings.volume import VoiceVolumeSettings


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
def voice_volume_settings() -> VoiceVolumeSettings:
    return VoiceVolumeSettings(1.0)


@pytest.fixture
def client(
    mock_connection_service: MagicMock,
    voice_volume_settings: VoiceVolumeSettings,
) -> TestClient:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        voice_pipeline=None,
        voice_volume_settings=voice_volume_settings,
    )
    with TestClient(app) as test_client:
        yield test_client


def test_get_volume_defaults_to_full_scale(client: TestClient) -> None:
    response = client.get("/settings/volume")

    assert response.status_code == 200
    assert response.json() == {"volume": 1.0}


def test_update_volume(
    client: TestClient,
    voice_volume_settings: VoiceVolumeSettings,
) -> None:
    response = client.put("/settings/volume", json={"volume": 1.75})

    assert response.status_code == 200
    assert response.json() == {"volume": 1.75}
    assert voice_volume_settings.volume == 1.75


def test_update_volume_rejects_out_of_range(client: TestClient) -> None:
    response = client.put("/settings/volume", json={"volume": 2.5})

    assert response.status_code == 422
