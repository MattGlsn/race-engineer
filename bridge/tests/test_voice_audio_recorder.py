from unittest.mock import MagicMock

import pytest

from race_engineer.voice.audio.models import AudioBuffer
from race_engineer.voice.audio.recorder import AudioRecorder, RecordingError


class FakeStream:
    def __init__(self, *, callback: MagicMock) -> None:
        self.callback = callback

    def start(self) -> None:
        self.callback(b"\x01\x00", 1, None, None)
        self.callback(b"\x02\x00", 1, None, None)

    def stop(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_audio_buffer_duration_seconds() -> None:
    buffer = AudioBuffer(
        pcm_bytes=b"\x00" * 32_000,
        sample_rate=16_000,
        channels=1,
        sample_width=2,
    )

    assert buffer.duration_seconds == pytest.approx(1.0)


def test_recorder_captures_pcm_chunks() -> None:
    sd = MagicMock()

    def raw_input_stream_factory(**kwargs: object) -> FakeStream:
        return FakeStream(callback=kwargs["callback"])  # type: ignore[arg-type]

    sd.RawInputStream.side_effect = raw_input_stream_factory

    recorder = AudioRecorder(sd=sd)
    recorder.start()
    buffer = recorder.stop()

    sd.RawInputStream.assert_called_once()
    _, kwargs = sd.RawInputStream.call_args
    assert kwargs["samplerate"] == 16_000
    assert kwargs["channels"] == 1
    assert kwargs["dtype"] == "int16"
    assert buffer.pcm_bytes == b"\x01\x00\x02\x00"


def test_recorder_stop_returns_joined_buffer() -> None:
    sd = MagicMock()

    def raw_input_stream_factory(**kwargs: object) -> FakeStream:
        return FakeStream(callback=kwargs["callback"])  # type: ignore[arg-type]

    sd.RawInputStream.side_effect = raw_input_stream_factory

    recorder = AudioRecorder(sd=sd)
    recorder.start()
    buffer = recorder.stop()

    assert buffer.pcm_bytes == b"\x01\x00\x02\x00"
    assert buffer.sample_rate == 16_000
    assert not recorder.is_recording


def test_recorder_rejects_double_start() -> None:
    sd = MagicMock()
    sd.RawInputStream.return_value = FakeStream(callback=MagicMock())

    recorder = AudioRecorder(sd=sd)
    recorder.start()

    with pytest.raises(RecordingError, match="already in progress"):
        recorder.start()


def test_recorder_rejects_stop_without_start() -> None:
    recorder = AudioRecorder(sd=MagicMock())

    with pytest.raises(RecordingError, match="not in progress"):
        recorder.stop()
