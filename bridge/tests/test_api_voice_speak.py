from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.connection import SdkConnectionService
from race_engineer.voice.engineer import EngineerVoiceService
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.tts.models import SynthesisResult


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
def mock_engineer_voice() -> MagicMock:
    return MagicMock(spec=EngineerVoiceService)


@pytest.fixture
def client(
    mock_connection_service: MagicMock,
    mock_engineer_voice: MagicMock,
) -> TestClient:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        engineer_voice=mock_engineer_voice,
    )
    with TestClient(app) as test_client:
        yield test_client


def test_speak_voice_returns_success(
    client: TestClient,
    mock_engineer_voice: MagicMock,
) -> None:
    mock_engineer_voice.speak.return_value = VoicePipelineResult.ok(
        SynthesisResult(text="stay out")
    )

    response = client.post("/voice/speak", json={"text": "stay out"})

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["text"] == "stay out"
    mock_engineer_voice.speak.assert_called_once_with("stay out")


def test_speak_voice_maps_provider_error(
    client: TestClient,
    mock_engineer_voice: MagicMock,
) -> None:
    mock_engineer_voice.speak.return_value = VoicePipelineResult.fail(
        error_code=VoiceErrorCode.NETWORK,
        message="connection reset",
    )

    response = client.post("/voice/speak", json={"text": "stay out"})

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail["success"] is False
    assert detail["error_code"] == "network"


def test_speak_voice_unconfigured_returns_503(
    mock_connection_service: MagicMock,
) -> None:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        engineer_voice=None,
    )
    app.state.engineer_voice = None

    with TestClient(app) as client:
        response = client.post("/voice/speak", json={"text": "stay out"})

    assert response.status_code == 503
