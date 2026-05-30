from __future__ import annotations

import os
from dataclasses import dataclass

from race_engineer.voice.hotkey.binding import HotkeyBinding
from race_engineer.voice.hotkey.errors import HotkeyConflictError
from race_engineer.voice.hotkey.joystick_binding import JoystickBinding

DEFAULT_VOICE_HOTKEY = "ctrl+shift+space"


@dataclass(frozen=True, slots=True)
class VoiceHotkeyConfig:
    binding: HotkeyBinding


def load_voice_hotkey_config() -> VoiceHotkeyConfig:
    raw = os.environ.get("VOICE_HOTKEY", DEFAULT_VOICE_HOTKEY).strip()
    if not raw:
        raise HotkeyConflictError("VOICE_HOTKEY must not be empty")

    try:
        binding = HotkeyBinding.parse(raw)
    except ValueError as exc:
        raise HotkeyConflictError(f"invalid VOICE_HOTKEY: {exc}") from exc

    return VoiceHotkeyConfig(binding=binding)


def load_joystick_ptt_config() -> JoystickBinding | None:
    raw = os.environ.get("VOICE_JOYSTICK_PTT", "").strip()
    if not raw:
        return None

    try:
        return JoystickBinding.parse(raw)
    except ValueError as exc:
        raise HotkeyConflictError(f"invalid VOICE_JOYSTICK_PTT: {exc}") from exc
