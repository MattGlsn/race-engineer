import os
from unittest.mock import patch

import numpy as np
import pytest

from race_engineer.voice.audio.volume import (
    VoiceVolumeConfig,
    apply_volume_to_pcm,
    load_voice_volume_config,
)


def test_apply_volume_to_pcm_scales_without_clipping() -> None:
    pcm = np.array([1000, -2000, 32767, -32768], dtype=np.int16).tobytes()

    result = apply_volume_to_pcm(pcm, 0.5)
    samples = np.frombuffer(result, dtype=np.int16)

    assert samples.tolist() == [500, -1000, 16383, -16384]


def test_apply_volume_to_pcm_full_scale_is_noop() -> None:
    pcm = b"\x00\x01\xff\x7f"

    assert apply_volume_to_pcm(pcm, 1.0) is pcm


def test_apply_volume_to_pcm_empty_buffer() -> None:
    assert apply_volume_to_pcm(b"", 0.5) == b""


def test_voice_volume_config_rejects_out_of_range() -> None:
    with pytest.raises(ValueError, match="volume must be between"):
        VoiceVolumeConfig(volume=1.5)


def test_load_voice_volume_config_defaults_to_full_scale() -> None:
    with patch.dict(os.environ, {}, clear=True):
        config = load_voice_volume_config()

    assert config.volume == 1.0


def test_load_voice_volume_config_reads_env() -> None:
    with patch.dict(os.environ, {"VOICE_OUTPUT_VOLUME": "0.25"}):
        config = load_voice_volume_config()

    assert config.volume == 0.25


def test_load_voice_volume_config_rejects_invalid_env() -> None:
    with patch.dict(os.environ, {"VOICE_OUTPUT_VOLUME": "loud"}):
        with pytest.raises(ValueError, match="must be a number"):
            load_voice_volume_config()
