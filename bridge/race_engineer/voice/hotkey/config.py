from __future__ import annotations

import os
from dataclasses import dataclass

from race_engineer.voice.hotkey.binding import HotkeyBinding
from race_engineer.voice.hotkey.errors import HotkeyConflictError

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
