import os
from unittest.mock import patch

import pytest

from race_engineer.voice.hotkey.config import load_joystick_ptt_config
from race_engineer.voice.hotkey.errors import HotkeyConflictError


def test_load_joystick_ptt_config_returns_none_when_unset() -> None:
    with patch.dict(os.environ, {}, clear=True):
        assert load_joystick_ptt_config() is None


def test_load_joystick_ptt_config_parses_binding() -> None:
    with patch.dict(os.environ, {"VOICE_JOYSTICK_PTT": "0:12"}, clear=True):
        binding = load_joystick_ptt_config()
        assert binding is not None
        assert binding.device == 0
        assert binding.kind == "button"
        assert binding.index == 12


def test_load_joystick_ptt_config_rejects_invalid_spec() -> None:
    with patch.dict(os.environ, {"VOICE_JOYSTICK_PTT": "bad"}, clear=True):
        with pytest.raises(HotkeyConflictError, match="invalid VOICE_JOYSTICK_PTT"):
            load_joystick_ptt_config()
