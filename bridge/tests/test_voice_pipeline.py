from unittest.mock import MagicMock

import pytest

from race_engineer.voice.audio.models import AudioBuffer
from race_engineer.voice.audio.recorder import AudioRecorder, RecordingError
from race_engineer.voice.pipeline import VoicePipeline
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult


@pytest.fixture
def stt_client() -> MagicMock:
    return MagicMock()


@pytest.fixture
def pipeline(stt_client: MagicMock) -> VoicePipeline:
    return VoicePipeline(stt_client, recorder=MagicMock(spec=AudioRecorder))


def test_transcribe_buffer_returns_transcript_with_duration(
    pipeline: VoicePipeline,
    stt_client: MagicMock,
) -> None:
    buffer = AudioBuffer(
        pcm_bytes=b"\x00" * 3_200,
        sample_rate=16_000,
    )
    stt_client.transcribe.return_value = VoicePipelineResult.ok(
        TranscriptResult(text="pit now", language_code="en")
    )

    result = pipeline.transcribe_buffer(buffer)

    assert result.success is True
    assert result.data is not None
    assert result.data.text == "pit now"
    assert result.data.duration_ms == 100
    stt_client.transcribe.assert_called_once()


def test_transcribe_buffer_rejects_empty_audio(pipeline: VoicePipeline) -> None:
    buffer = AudioBuffer(pcm_bytes=b"", sample_rate=16_000)

    result = pipeline.transcribe_buffer(buffer)

    assert result.success is False
    assert result.error_code == VoiceErrorCode.EMPTY_AUDIO


def test_transcribe_from_microphone_uses_recorder(
    pipeline: VoicePipeline,
    stt_client: MagicMock,
) -> None:
    recorder = pipeline._recorder
    recorder.start.return_value = None
    recorder.stop.return_value = AudioBuffer(
        pcm_bytes=b"\x00" * 3_200,
        sample_rate=16_000,
    )
    stt_client.transcribe.return_value = VoicePipelineResult.ok(
        TranscriptResult(text="fuel check", language_code="en")
    )

    result = pipeline.transcribe_from_microphone()

    assert result.success is True
    assert result.data is not None
    assert result.data.text == "fuel check"
    recorder.start.assert_called_once()
    recorder.stop.assert_called_once()


def test_start_and_stop_and_transcribe(
    pipeline: VoicePipeline,
    stt_client: MagicMock,
) -> None:
    recorder = pipeline._recorder
    recorder.start.return_value = None
    recorder.stop.return_value = AudioBuffer(
        pcm_bytes=b"\x00" * 3_200,
        sample_rate=16_000,
    )
    stt_client.transcribe.return_value = VoicePipelineResult.ok(
        TranscriptResult(text="clear", language_code="en")
    )

    pipeline.start_recording()
    result = pipeline.stop_and_transcribe()

    assert result.success is True
    assert result.data is not None
    assert result.data.text == "clear"
    recorder.start.assert_called_once()
    recorder.stop.assert_called_once()


def test_transcribe_from_microphone_maps_recording_errors(
    pipeline: VoicePipeline,
) -> None:
    recorder = pipeline._recorder
    recorder.start.side_effect = RecordingError("recording already in progress")

    result = pipeline.transcribe_from_microphone()

    assert result.success is False
    assert result.error_code == VoiceErrorCode.PROVIDER_ERROR
