import logging
from unittest.mock import MagicMock

import httpx
import pytest

from race_engineer.voice.stt.client import ElevenLabsSttClient
from race_engineer.voice.stt.config import ElevenLabsSttConfig
from race_engineer.voice.stt.errors import VoiceErrorCode


@pytest.fixture
def config() -> ElevenLabsSttConfig:
    return ElevenLabsSttConfig(api_key="test-key", model_id="scribe_v2")


def test_transcribe_returns_transcript(config: ElevenLabsSttConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.return_value = httpx.Response(
        200,
        json={
            "text": "box box box",
            "language_code": "eng",
            "audio_duration_secs": 1.25,
        },
    )

    client = ElevenLabsSttClient(config, http_client=http_client)
    result = client.transcribe(b"RIFF....WAVE")

    assert result.success is True
    assert result.data is not None
    assert result.data.text == "box box box"
    assert result.data.language_code == "eng"
    assert result.data.duration_ms == 1250

    http_client.post.assert_called_once()
    args, kwargs = http_client.post.call_args
    assert args[0] == "https://api.elevenlabs.io/v1/speech-to-text"
    assert kwargs["headers"]["xi-api-key"] == "test-key"
    assert kwargs["data"]["model_id"] == "scribe_v2"
    assert kwargs["data"]["language_code"] == "en"
    assert kwargs["files"]["file"][0] == "audio.wav"


def test_transcribe_logs_transcript(config: ElevenLabsSttConfig, caplog) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.return_value = httpx.Response(
        200,
        json={
            "text": "box box box",
            "language_code": "eng",
            "audio_duration_secs": 1.25,
        },
    )

    client = ElevenLabsSttClient(config, http_client=http_client)

    with caplog.at_level(logging.INFO):
        client.transcribe(b"RIFF....WAVE")

    assert "box box box" in caplog.text
    assert "elevenlabs stt transcript" in caplog.text


def test_transcribe_rejects_empty_wav(config: ElevenLabsSttConfig) -> None:
    client = ElevenLabsSttClient(config, http_client=MagicMock(spec=httpx.Client))

    result = client.transcribe(b"")

    assert result.success is False
    assert result.error_code == VoiceErrorCode.EMPTY_AUDIO


def test_transcribe_maps_invalid_api_key(config: ElevenLabsSttConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.return_value = httpx.Response(401, json={"detail": "invalid api key"})

    client = ElevenLabsSttClient(config, http_client=http_client)
    result = client.transcribe(b"RIFF....WAVE")

    assert result.success is False
    assert result.error_code == VoiceErrorCode.INVALID_API_KEY


def test_transcribe_maps_rate_limit(config: ElevenLabsSttConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.return_value = httpx.Response(429, json={"detail": "too many requests"})

    client = ElevenLabsSttClient(config, http_client=http_client)
    result = client.transcribe(b"RIFF....WAVE")

    assert result.success is False
    assert result.error_code == VoiceErrorCode.RATE_LIMIT


def test_transcribe_maps_server_error(config: ElevenLabsSttConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.return_value = httpx.Response(503, json={"detail": "unavailable"})

    client = ElevenLabsSttClient(config, http_client=http_client)
    result = client.transcribe(b"RIFF....WAVE")

    assert result.success is False
    assert result.error_code == VoiceErrorCode.PROVIDER_ERROR


def test_transcribe_maps_network_timeout(config: ElevenLabsSttConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.side_effect = httpx.TimeoutException("timed out")

    client = ElevenLabsSttClient(config, http_client=http_client)
    result = client.transcribe(b"RIFF....WAVE")

    assert result.success is False
    assert result.error_code == VoiceErrorCode.NETWORK
