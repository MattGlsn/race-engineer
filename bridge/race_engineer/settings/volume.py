from race_engineer.voice.audio.volume import (
    DEFAULT_VOICE_OUTPUT_VOLUME,
    MAX_VOICE_OUTPUT_VOLUME,
    validate_voice_output_volume,
)


class VoiceVolumeSettings:
    """In-memory engineer TTS playback gain (0.0–2.0, shared by API and voice pipeline)."""

    def __init__(self, volume: float | None = None) -> None:
        self._volume = validate_voice_output_volume(
            volume if volume is not None else DEFAULT_VOICE_OUTPUT_VOLUME
        )

    @property
    def volume(self) -> float:
        return self._volume

    def set_volume(self, volume: float) -> None:
        self._volume = validate_voice_output_volume(volume)
