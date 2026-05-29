from unittest.mock import MagicMock

import pytest

from race_engineer.voice.audio.recorder import RecordingError
from race_engineer.voice.hotkey.controller import VoiceHotkeyController
from race_engineer.voice.pipeline import VoicePipeline
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult


@pytest.fixture
def pipeline() -> MagicMock:
    mock = MagicMock(spec=VoicePipeline)
    mock.recorder = MagicMock()
    mock.recorder.is_recording = False
    return mock


def test_press_starts_recording_when_idle(pipeline: MagicMock) -> None:
    controller = VoiceHotkeyController(pipeline)

    controller.on_press()

    pipeline.start_recording.assert_called_once()
    assert controller.is_ptt_active


def test_press_ignored_when_already_active(pipeline: MagicMock) -> None:
    pipeline.recorder.is_recording = True
    controller = VoiceHotkeyController(pipeline)
    controller.on_press()
    pipeline.reset_mock()
    pipeline.recorder.is_recording = True

    controller.on_press()

    pipeline.start_recording.assert_not_called()


def test_press_ignored_after_recording_error(pipeline: MagicMock) -> None:
    pipeline.start_recording.side_effect = RecordingError("recording already in progress")
    controller = VoiceHotkeyController(pipeline)

    controller.on_press()

    assert not controller.is_ptt_active


def test_release_ignored_without_active_press(pipeline: MagicMock) -> None:
    controller = VoiceHotkeyController(pipeline)

    controller.on_release()

    pipeline.stop_and_transcribe.assert_not_called()


def test_release_stops_and_invokes_callback(pipeline: MagicMock) -> None:
    callback = MagicMock()
    controller = VoiceHotkeyController(pipeline, on_transcript=callback)
    controller.on_press()
    result = VoicePipelineResult.ok(
        TranscriptResult(text="pit now", language_code="en", duration_ms=100)
    )
    pipeline.stop_and_transcribe.return_value = result

    controller.on_release()

    pipeline.stop_and_transcribe.assert_called_once()
    callback.assert_called_once_with(result)
