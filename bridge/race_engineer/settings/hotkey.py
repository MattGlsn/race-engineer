from __future__ import annotations

from race_engineer.voice.hotkey.binding import HotkeyBinding
from race_engineer.voice.hotkey.config import DEFAULT_VOICE_HOTKEY, load_voice_hotkey_config


class VoiceHotkeySettings:
    """In-memory push-to-talk hotkey preference shared by API and hotkey service."""

    def __init__(self, binding: HotkeyBinding | None = None) -> None:
        if binding is None:
            binding = load_voice_hotkey_config().binding
        self._binding = binding

    @property
    def binding(self) -> HotkeyBinding:
        return self._binding

    @property
    def spec(self) -> str:
        return self._binding.format()

    def set_binding(self, binding: HotkeyBinding) -> None:
        self._binding = binding

    @classmethod
    def from_env(cls) -> VoiceHotkeySettings:
        return cls(load_voice_hotkey_config().binding)


DEFAULT_VOICE_HOTKEY_SPEC = DEFAULT_VOICE_HOTKEY
