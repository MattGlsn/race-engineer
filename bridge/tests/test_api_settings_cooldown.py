from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.connection import SdkConnectionService
from race_engineer.proactive.triggers.models import TriggerType
from race_engineer.settings.cooldown import CooldownSettings


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
def cooldown_settings() -> CooldownSettings:
    return CooldownSettings()


@pytest.fixture
def client(
    mock_connection_service: MagicMock,
    cooldown_settings: CooldownSettings,
) -> TestClient:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        voice_pipeline=None,
        cooldown_settings=cooldown_settings,
    )
    with TestClient(app) as test_client:
        yield test_client


def test_get_cooldown_returns_defaults(client: TestClient) -> None:
    response = client.get("/settings/cooldown")

    assert response.status_code == 200
    payload = response.json()
    assert payload["global_interval_seconds"] == 10.0
    assert payload["trigger_intervals_seconds"]["fuel"] == 60.0
    assert payload["trigger_intervals_seconds"]["incident"] == 30.0


def test_update_cooldown(
    client: TestClient,
    cooldown_settings: CooldownSettings,
) -> None:
    response = client.put(
        "/settings/cooldown",
        json={
            "global_interval_seconds": 5.0,
            "trigger_intervals_seconds": {"fuel": 90.0},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["global_interval_seconds"] == 5.0
    assert payload["trigger_intervals_seconds"]["fuel"] == 90.0
    assert cooldown_settings.config.global_interval_seconds == 5.0
    assert cooldown_settings.config.interval_for(TriggerType.FUEL) == 90.0


def test_update_cooldown_rejects_unknown_trigger(client: TestClient) -> None:
    response = client.put(
        "/settings/cooldown",
        json={"trigger_intervals_seconds": {"unknown": 10.0}},
    )

    assert response.status_code == 422
