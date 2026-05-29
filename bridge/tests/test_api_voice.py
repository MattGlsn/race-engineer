from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.connection import SdkConnectionService
from race_engineer.voice.pipeline import VoicePipeline
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult


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
def mock_voice_pipeline() -> MagicMock:
    return MagicMock(spec=VoicePipeline)


@pytest.fixture
def client(
    mock_connection_service: MagicMock,
    mock_voice_pipeline: MagicMock,
) -> TestClient:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        voice_pipeline=mock_voice_pipeline,
    )
    with TestClient(app) as test_client:
        yield test_client


def test_transcribe_voice_returns_transcript(
    client: TestClient,
    mock_voice_pipeline: MagicMock,
) -> None:
    mock_voice_pipeline.transcribe_wav.return_value = VoicePipelineResult.ok(
        TranscriptResult(text="stay out", language_code="en", duration_ms=500)
    )

    response = client.post(
        "/voice/transcribe",
        files={"file": ("clip.wav", b"RIFF....WAVE", "audio/wav")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["text"] == "stay out"
    assert data["language_code"] == "en"
    mock_voice_pipeline.transcribe_wav.assert_called_once_with(b"RIFF....WAVE")


def test_transcribe_voice_maps_provider_error(
    client: TestClient,
    mock_voice_pipeline: MagicMock,
) -> None:
    mock_voice_pipeline.transcribe_wav.return_value = VoicePipelineResult.fail(
        error_code=VoiceErrorCode.NETWORK,
        message="connection reset",
    )

    response = client.post(
        "/voice/transcribe",
        files={"file": ("clip.wav", b"RIFF....WAVE", "audio/wav")},
    )

    assert response.status_code == 502
    detail = response.json()["detail"]
    assert detail["success"] is False
    assert detail["error_code"] == "network"


def test_transcribe_voice_unconfigured_returns_503(
    mock_connection_service: MagicMock,
) -> None:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        voice_pipeline=None,
    )
    app.state.voice_pipeline = None

    with TestClient(app) as client:
        response = client.post(
            "/voice/transcribe",
            files={"file": ("clip.wav", b"RIFF....WAVE", "audio/wav")},
        )

    assert response.status_code == 503
