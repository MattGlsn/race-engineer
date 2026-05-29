from __future__ import annotations

import os
from dataclasses import dataclass

import numpy as np

DEFAULT_VOICE_OUTPUT_VOLUME = 1.0
MAX_VOICE_OUTPUT_VOLUME = 2.0


def validate_voice_output_volume(volume: float) -> float:
    if not 0.0 <= volume <= MAX_VOICE_OUTPUT_VOLUME:
        raise ValueError(
            f"volume must be between 0.0 and {MAX_VOICE_OUTPUT_VOLUME}"
        )
    return volume


@dataclass(frozen=True, slots=True)
class VoiceVolumeConfig:
    """Output gain for engineer TTS playback (0.0 = silent, 2.0 = boosted)."""

    volume: float = DEFAULT_VOICE_OUTPUT_VOLUME

    def __post_init__(self) -> None:
        validate_voice_output_volume(self.volume)


def load_voice_volume_config() -> VoiceVolumeConfig:
    raw = os.environ.get("VOICE_OUTPUT_VOLUME")
    if raw is None:
        return VoiceVolumeConfig()

    try:
        volume = float(raw)
    except ValueError as exc:
        raise ValueError("VOICE_OUTPUT_VOLUME must be a number") from exc

    return VoiceVolumeConfig(volume=volume)


def apply_volume_to_pcm(pcm_bytes: bytes, volume: float) -> bytes:
    """Scale int16 PCM samples and clamp to prevent clipping."""
    if not pcm_bytes:
        return pcm_bytes

    clamped_volume = max(0.0, min(MAX_VOICE_OUTPUT_VOLUME, volume))
    if clamped_volume == 1.0:
        return pcm_bytes

    samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
    scaled = np.clip(samples * clamped_volume, -32767.0, 32767.0).astype(np.int16)
    return scaled.tobytes()
