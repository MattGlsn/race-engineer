from unittest.mock import MagicMock

import pytest

from race_engineer.voice.audio.models import AudioBuffer
from race_engineer.voice.audio.recorder import (
    AudioRecorder,
    RecordingError,
    resolve_input_settings,
)


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


def _mock_sd_with_input(*, default_index: int = 0) -> MagicMock:
    sd = MagicMock()
    sd.default.device = (default_index, 1)
    sd.query_devices.return_value = [
        {"index": 0, "max_input_channels": 2, "name": "Mic", "default_samplerate": 16_000.0},
        {"index": 1, "max_input_channels": 0, "name": "Speakers", "default_samplerate": 44_100.0},
    ]
    sd.query_devices.side_effect = lambda device=None: (
        sd.query_devices.return_value[device]
        if isinstance(device, int)
        else sd.query_devices.return_value
    )
    sd.check_input_settings.return_value = None
    return sd


def test_audio_buffer_duration_seconds() -> None:
    buffer = AudioBuffer(
        pcm_bytes=b"\x00" * 32_000,
        sample_rate=16_000,
        channels=1,
        sample_width=2,
    )

    assert buffer.duration_seconds == pytest.approx(1.0)


def test_recorder_captures_pcm_chunks() -> None:
    sd = _mock_sd_with_input()

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
    assert kwargs["device"] == 0
    assert buffer.pcm_bytes == b"\x01\x00\x02\x00"


def test_recorder_stop_returns_joined_buffer() -> None:
    sd = _mock_sd_with_input()

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
    sd = _mock_sd_with_input()
    sd.RawInputStream.return_value = FakeStream(callback=MagicMock())

    recorder = AudioRecorder(sd=sd)
    recorder.start()

    with pytest.raises(RecordingError, match="already in progress"):
        recorder.start()


def test_recorder_rejects_stop_without_start() -> None:
    recorder = AudioRecorder(sd=MagicMock())

    with pytest.raises(RecordingError, match="not in progress"):
        recorder.stop()


def test_resolve_input_settings_uses_first_input_when_default_invalid() -> None:
    sd = MagicMock()
    sd.default.device = (-1, -1)
    sd.query_devices.return_value = [
        {"index": 0, "max_input_channels": 0, "name": "Speakers", "default_samplerate": 44_100.0},
        {"index": 1, "max_input_channels": 1, "name": "Mic", "default_samplerate": 44_100.0},
    ]
    sd.query_devices.side_effect = lambda device=None: (
        sd.query_devices.return_value[device]
        if isinstance(device, int)
        else sd.query_devices.return_value
    )
    sd.check_input_settings.return_value = None

    assert resolve_input_settings(sd, sample_rate=16_000, channels=1) == (1, 16_000)


def test_resolve_input_settings_raises_when_none_available() -> None:
    sd = MagicMock()
    sd.default.device = (-1, -1)
    sd.query_devices.return_value = [
        {"index": 0, "max_input_channels": 0, "name": "Speakers", "default_samplerate": 44_100.0},
    ]
    sd.query_devices.side_effect = lambda device=None: (
        sd.query_devices.return_value[device]
        if isinstance(device, int)
        else sd.query_devices.return_value
    )

    with pytest.raises(RecordingError, match="no microphone input device available"):
        resolve_input_settings(sd, sample_rate=16_000, channels=1)


def test_resolve_input_settings_honors_env_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sd = MagicMock()
    sd.query_devices.return_value = {
        "index": 2,
        "max_input_channels": 2,
        "name": "Mic",
        "default_samplerate": 16_000.0,
    }
    sd.check_input_settings.return_value = None

    monkeypatch.setenv("VOICE_INPUT_DEVICE", "2")

    assert resolve_input_settings(sd, sample_rate=16_000, channels=1) == (2, 16_000)
    sd.query_devices.assert_called_with(2)


def test_resolve_input_settings_rejects_invalid_env_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sd = MagicMock()
    sd.query_devices.side_effect = Exception("invalid device")

    monkeypatch.setenv("VOICE_INPUT_DEVICE", "99")

    with pytest.raises(
        RecordingError,
        match="VOICE_INPUT_DEVICE 99 is not a valid input device",
    ):
        resolve_input_settings(sd, sample_rate=16_000, channels=1)


def test_resolve_input_settings_falls_back_to_supported_sample_rate() -> None:
    sd = MagicMock()
    sd.default.device = (-1, -1)
    sd.query_devices.return_value = [
        {
            "index": 19,
            "max_input_channels": 2,
            "name": "Microphone (Mic in at front panel (black))",
            "default_samplerate": 44_100.0,
        },
    ]
    sd.query_devices.side_effect = lambda device=None: (
        sd.query_devices.return_value[0]
        if isinstance(device, int)
        else sd.query_devices.return_value
    )

    def check_input_settings(**kwargs: object) -> None:
        if kwargs["samplerate"] == 16_000:
            raise Exception("Invalid sample rate")
        if kwargs["samplerate"] == 44_100:
            return None
        raise Exception("Invalid sample rate")

    sd.check_input_settings.side_effect = check_input_settings

    assert resolve_input_settings(sd, sample_rate=16_000, channels=1) == (19, 44_100)


def test_resolve_input_settings_prefers_microphone_over_stereo_mix() -> None:
    sd = MagicMock()
    sd.default.device = (-1, -1)
    sd.query_devices.return_value = [
        {
            "index": 18,
            "max_input_channels": 2,
            "name": "Stereo Mix (Realtek HD Audio Stereo input)",
            "default_samplerate": 48_000.0,
        },
        {
            "index": 19,
            "max_input_channels": 2,
            "name": "Microphone (Mic in at front panel (black))",
            "default_samplerate": 44_100.0,
        },
    ]
    sd.query_devices.side_effect = lambda device=None: (
        sd.query_devices.return_value[device - 18]
        if isinstance(device, int)
        else sd.query_devices.return_value
    )
    sd.check_input_settings.return_value = None

    assert resolve_input_settings(sd, sample_rate=16_000, channels=1)[0] == 19


def test_recorder_uses_fallback_sample_rate_in_buffer() -> None:
    sd = MagicMock()
    sd.default.device = (-1, -1)
    sd.query_devices.return_value = [
        {
            "index": 19,
            "max_input_channels": 2,
            "name": "Microphone",
            "default_samplerate": 44_100.0,
        },
    ]
    sd.query_devices.side_effect = lambda device=None: (
        sd.query_devices.return_value[0]
        if isinstance(device, int)
        else sd.query_devices.return_value
    )

    def check_input_settings(**kwargs: object) -> None:
        if kwargs["samplerate"] == 16_000:
            raise Exception("Invalid sample rate")
        if kwargs["samplerate"] == 44_100:
            return None
        raise Exception("Invalid sample rate")

    sd.check_input_settings.side_effect = check_input_settings
    sd.RawInputStream.return_value = FakeStream(callback=MagicMock())

    recorder = AudioRecorder(sd=sd)
    recorder.start()
    buffer = recorder.stop()

    _, kwargs = sd.RawInputStream.call_args
    assert kwargs["samplerate"] == 44_100
    assert buffer.sample_rate == 44_100


def test_recorder_wraps_portaudio_errors() -> None:
    sd = _mock_sd_with_input()
    sd.RawInputStream.side_effect = Exception("Error querying device -1")

    recorder = AudioRecorder(sd=sd)

    with pytest.raises(RecordingError, match="Error querying device -1"):
        recorder.start()

    assert not recorder.is_recording
