from __future__ import annotations

from typing import Any

from race_engineer.voice.audio.models import (
    DEFAULT_CHANNELS,
    DEFAULT_SAMPLE_RATE,
    AudioBuffer,
)


class RecordingError(Exception):
    """Raised when start/stop recording is invoked in an invalid state."""


class AudioRecorder:
    """Captures microphone input into an in-memory PCM buffer."""

    def __init__(
        self,
        *,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        channels: int = DEFAULT_CHANNELS,
        sd: Any | None = None,
    ) -> None:
        self._sample_rate = sample_rate
        self._channels = channels
        self._sd = sd
        self._stream: Any | None = None
        self._chunks: list[bytes] = []

    @property
    def is_recording(self) -> bool:
        return self._stream is not None

    def start(self) -> None:
        if self._stream is not None:
            raise RecordingError("recording already in progress")

        sd = self._resolve_sounddevice()
        self._chunks = []

        def callback(indata: bytes, frames: int, time_info: Any, status: Any) -> None:
            del frames, time_info, status
            self._chunks.append(bytes(indata))

        self._stream = sd.RawInputStream(
            samplerate=self._sample_rate,
            channels=self._channels,
            dtype="int16",
            callback=callback,
        )
        self._stream.start()

    def stop(self) -> AudioBuffer:
        if self._stream is None:
            raise RecordingError("recording is not in progress")

        self._stream.stop()
        self._stream.close()
        self._stream = None

        return AudioBuffer(
            pcm_bytes=b"".join(self._chunks),
            sample_rate=self._sample_rate,
            channels=self._channels,
        )

    def _resolve_sounddevice(self) -> Any:
        if self._sd is not None:
            return self._sd

        import sounddevice as sd_module

        return sd_module
