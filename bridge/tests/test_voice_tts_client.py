from unittest.mock import MagicMock

import httpx
import pytest

from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.tts.client import ElevenLabsTtsClient
from race_engineer.voice.tts.config import ElevenLabsTtsConfig


@pytest.fixture
def config() -> ElevenLabsTtsConfig:
    return ElevenLabsTtsConfig(
        api_key="test-key",
        voice_id="voice-123",
        model_id="eleven_turbo_v2_5",
        output_format="pcm_16000",
    )


def test_synthesize_stream_returns_pcm_chunks(config: ElevenLabsTtsConfig) -> None:
    response = MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.iter_bytes.return_value = iter([b"\x00\x01", b"\x02\x03"])

    stream_cm = MagicMock()
    stream_cm.__enter__.return_value = response

    http_client = MagicMock(spec=httpx.Client)
    http_client.stream.return_value = stream_cm

    client = ElevenLabsTtsClient(config, http_client=http_client)
    result = client.synthesize_stream("stay out")

    assert result.success
    assert result.data is not None
    assert b"".join(result.data) == b"\x00\x01\x02\x03"

    args, kwargs = http_client.stream.call_args
    assert args[0] == "POST"
    assert args[1].endswith("/v1/text-to-speech/voice-123/stream")
    assert kwargs["params"]["output_format"] == "pcm_16000"
    assert kwargs["json"]["text"] == "stay out"
    stream_cm.__exit__.assert_called_once()


def test_synthesize_stream_rejects_empty_text(config: ElevenLabsTtsConfig) -> None:
    client = ElevenLabsTtsClient(config, http_client=MagicMock(spec=httpx.Client))

    result = client.synthesize_stream("   ")

    assert not result.success
    assert result.error_code == VoiceErrorCode.EMPTY_AUDIO


def test_synthesize_stream_maps_invalid_api_key(config: ElevenLabsTtsConfig) -> None:
    response = MagicMock(spec=httpx.Response)
    response.status_code = 401

    stream_cm = MagicMock()
    stream_cm.__enter__.return_value = response

    http_client = MagicMock(spec=httpx.Client)
    http_client.stream.return_value = stream_cm

    client = ElevenLabsTtsClient(config, http_client=http_client)
    result = client.synthesize_stream("hello")

    assert not result.success
    assert result.error_code == VoiceErrorCode.INVALID_API_KEY
    stream_cm.__exit__.assert_called_once()


def test_synthesize_stream_maps_rate_limit(config: ElevenLabsTtsConfig) -> None:
    response = MagicMock(spec=httpx.Response)
    response.status_code = 429

    stream_cm = MagicMock()
    stream_cm.__enter__.return_value = response

    http_client = MagicMock(spec=httpx.Client)
    http_client.stream.return_value = stream_cm

    client = ElevenLabsTtsClient(config, http_client=http_client)
    result = client.synthesize_stream("hello")

    assert not result.success
    assert result.error_code == VoiceErrorCode.RATE_LIMIT


def test_load_elevenlabs_tts_config_requires_voice_id() -> None:
    from race_engineer.voice.tts.config import load_elevenlabs_tts_config

    import os
    from unittest.mock import patch

    with patch.dict(os.environ, {"ELEVENLABS_API_KEY": "key"}, clear=True):
        assert load_elevenlabs_tts_config() is None
