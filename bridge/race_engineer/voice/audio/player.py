from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from race_engineer.voice.audio.models import DEFAULT_CHANNELS, DEFAULT_SAMPLE_RATE
from race_engineer.voice.audio.volume import apply_volume_to_pcm


class PlaybackError(Exception):
    """Raised when audio output cannot be started."""


class AudioPlayer:
    """Streams PCM chunks to the default output device."""

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

    def play_stream(
        self,
        chunks: Iterable[bytes],
        *,
        volume: float = 1.0,
    ) -> None:
        sd = self._resolve_sounddevice()
        try:
            with sd.RawOutputStream(
                samplerate=self._sample_rate,
                channels=self._channels,
                dtype="int16",
            ) as stream:
                stream.start()
                for chunk in chunks:
                    if not chunk:
                        continue
                    stream.write(apply_volume_to_pcm(chunk, volume))
                stream.stop()
        except Exception as exc:
            raise PlaybackError(str(exc)) from exc

    def _resolve_sounddevice(self) -> Any:
        if self._sd is not None:
            return self._sd

        import sounddevice as sd_module

        return sd_module
