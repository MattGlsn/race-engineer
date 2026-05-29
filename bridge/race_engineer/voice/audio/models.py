from dataclasses import dataclass

DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_CHANNELS = 1
DEFAULT_SAMPLE_WIDTH = 2


@dataclass(frozen=True, slots=True)
class AudioBuffer:
    """In-memory PCM audio captured from the microphone."""

    pcm_bytes: bytes
    sample_rate: int = DEFAULT_SAMPLE_RATE
    channels: int = DEFAULT_CHANNELS
    sample_width: int = DEFAULT_SAMPLE_WIDTH

    @property
    def duration_seconds(self) -> float:
        bytes_per_frame = self.sample_width * self.channels
        if bytes_per_frame <= 0:
            return 0.0
        frame_count = len(self.pcm_bytes) // bytes_per_frame
        if self.sample_rate <= 0:
            return 0.0
        return frame_count / self.sample_rate
