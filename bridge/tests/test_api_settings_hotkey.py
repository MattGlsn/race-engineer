from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.connection import SdkConnectionService
from race_engineer.settings.hotkey import VoiceHotkeySettings
from race_engineer.voice.hotkey.binding import HotkeyBinding


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
def hotkey_settings() -> VoiceHotkeySettings:
    return VoiceHotkeySettings(HotkeyBinding.parse("ctrl+shift+space"))


@pytest.fixture
def client(
    mock_connection_service: MagicMock,
    hotkey_settings: VoiceHotkeySettings,
) -> TestClient:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        voice_pipeline=None,
        hotkey_settings=hotkey_settings,
    )
    with TestClient(app) as test_client:
        yield test_client


def test_get_hotkey_defaults_to_ctrl_shift_space(client: TestClient) -> None:
    response = client.get("/settings/hotkey")

    assert response.status_code == 200
    assert response.json() == {"hotkey": "ctrl+shift+space"}


def test_update_hotkey(
    client: TestClient,
    hotkey_settings: VoiceHotkeySettings,
) -> None:
    response = client.put("/settings/hotkey", json={"hotkey": "ctrl+alt+v"})

    assert response.status_code == 200
    assert response.json() == {"hotkey": "alt+ctrl+v"}
    assert hotkey_settings.spec == "alt+ctrl+v"

    get_response = client.get("/settings/hotkey")
    assert get_response.json() == {"hotkey": "alt+ctrl+v"}


def test_update_hotkey_rejects_invalid_spec(client: TestClient) -> None:
    response = client.put("/settings/hotkey", json={"hotkey": "ctrl+a+b"})

    assert response.status_code == 422
