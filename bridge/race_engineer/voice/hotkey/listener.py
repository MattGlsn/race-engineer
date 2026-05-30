from __future__ import annotations

import logging
from typing import Any

from race_engineer.voice.hotkey.binding import HotkeyBinding
from race_engineer.voice.hotkey.controller import VoiceHotkeyController
from race_engineer.voice.hotkey.errors import HotkeyRegistrationError

logger = logging.getLogger(__name__)


def normalize_key(key: Any) -> str | None:
    """Map a pynput key event to a binding token name."""
    char = getattr(key, "char", None)
    if char:
        return char.lower()

    name = getattr(key, "name", None)
    if not name:
        return None

    lowered = name.lower()
    if lowered in {"ctrl_l", "ctrl_r"}:
        return "ctrl"
    if lowered in {"shift_l", "shift_r"}:
        return "shift"
    if lowered in {"alt_l", "alt_r", "alt_gr"}:
        return "alt"
    if lowered in {"cmd", "cmd_l", "cmd_r"}:
        return "cmd"
    if lowered in {"win", "win_l", "win_r"}:
        return "win"
    return lowered


class GlobalHotkeyListener:
    """Registers a global push-to-talk listener via pynput."""

    def __init__(
        self,
        binding: HotkeyBinding,
        controller: VoiceHotkeyController,
        *,
        keyboard_module: Any | None = None,
    ) -> None:
        self._binding = binding
        self._controller = controller
        self._keyboard_module = keyboard_module
        self._pressed: set[str] = set()
        self._combo_held = False
        self._listener: Any | None = None
        self._active = False

    def start(self) -> None:
        if self._listener is not None:
            raise HotkeyRegistrationError("hotkey listener already running")

        keyboard = self._resolve_keyboard()
        self._listener = keyboard.Listener(
            on_press=self._handle_press,
            on_release=self._handle_release,
        )
        try:
            self._listener.start()
        except Exception as exc:
            self._listener = None
            raise HotkeyRegistrationError(
                f"failed to start global hotkey listener: {exc}"
            ) from exc

        self._active = True
        logger.info(
            "global voice hotkey active: %s",
            "+".join(sorted(self._binding.modifiers) + [self._binding.key]),
        )

    def stop(self) -> None:
        self._active = False
        if self._listener is None:
            return

        self._listener.stop()
        self._listener = None
        self._pressed.clear()
        self._combo_held = False

    def _handle_press(self, key: Any) -> None:
        if not self._active:
            return
        token = normalize_key(key)
        if token is None:
            return

        self._pressed.add(token)
        if not self._combo_held and self._binding.matches(frozenset(self._pressed)):
            self._combo_held = True
            self._controller.on_press()

    def _handle_release(self, key: Any) -> None:
        if not self._active:
            return
        token = normalize_key(key)
        if token is None:
            return

        self._pressed.discard(token)

        if self._combo_held and not self._binding.matches(frozenset(self._pressed)):
            self._combo_held = False
            self._controller.on_release()

    def _resolve_keyboard(self) -> Any:
        if self._keyboard_module is not None:
            return self._keyboard_module

        from pynput import keyboard

        return keyboard
