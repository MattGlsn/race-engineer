import pytest

from race_engineer.voice.audio.models import AudioBuffer
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.stt.validation import MIN_AUDIO_DURATION_SECONDS, validate_audio


def test_validate_audio_accepts_valid_buffer() -> None:
    buffer = AudioBuffer(
        pcm_bytes=b"\x00" * int(16_000 * MIN_AUDIO_DURATION_SECONDS * 2),
        sample_rate=16_000,
    )

    assert validate_audio(buffer) == []


def test_validate_audio_rejects_empty_buffer() -> None:
    buffer = AudioBuffer(pcm_bytes=b"", sample_rate=16_000)

    assert validate_audio(buffer) == ["audio buffer is empty"]


def test_validate_audio_rejects_short_buffer() -> None:
    buffer = AudioBuffer(pcm_bytes=b"\x00\x00", sample_rate=16_000)

    errors = validate_audio(buffer)

    assert len(errors) == 1
    assert errors[0].startswith("audio too short:")


def test_voice_pipeline_result_ok() -> None:
    result = VoicePipelineResult.ok("hello")

    assert result.success is True
    assert result.data == "hello"
    assert result.error_code is None
    assert result.message is None


def test_voice_pipeline_result_fail() -> None:
    result = VoicePipelineResult.fail(
        error_code=VoiceErrorCode.NETWORK,
        message="connection reset",
    )

    assert result.success is False
    assert result.data is None
    assert result.error_code == VoiceErrorCode.NETWORK
    assert result.message == "connection reset"


@pytest.mark.parametrize(
    "code",
    list(VoiceErrorCode),
)
def test_voice_error_codes_are_strings(code: VoiceErrorCode) -> None:
    assert isinstance(code.value, str)
