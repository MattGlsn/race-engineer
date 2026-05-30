from __future__ import annotations

import logging
import threading
import time
from typing import Any

from race_engineer.voice.hotkey.controller import VoiceHotkeyController
from race_engineer.voice.hotkey.errors import HotkeyRegistrationError
from race_engineer.voice.hotkey.joystick_binding import JoystickBinding
from race_engineer.voice.hotkey.joystick_pygame import init_pygame_joystick

logger = logging.getLogger(__name__)

_POLL_INTERVAL_SECONDS = 0.01


class JoystickPttListener:
    """Polls steering-wheel / gamepad buttons for push-to-talk."""

    def __init__(
        self,
        binding: JoystickBinding,
        controller: VoiceHotkeyController,
        *,
        pygame_module: Any | None = None,
        poll_interval_seconds: float = _POLL_INTERVAL_SECONDS,
    ) -> None:
        self._binding = binding
        self._controller = controller
        self._pygame_module = pygame_module
        self._poll_interval_seconds = poll_interval_seconds
        self._thread: threading.Thread | None = None
        self._joystick: Any | None = None
        self._active = False
        self._held = False
        self._stop_event = threading.Event()

    def start(self) -> None:
        if self._thread is not None:
            raise HotkeyRegistrationError("joystick listener already running")

        pygame = self._resolve_pygame()
        try:
            init_pygame_joystick(pygame)
        except Exception as exc:
            raise HotkeyRegistrationError(
                f"failed to initialize pygame joystick support: {exc}"
            ) from exc

        device_count = pygame.joystick.get_count()
        if self._binding.device >= device_count:
            raise HotkeyRegistrationError(
                "joystick device "
                f"{self._binding.device} not found "
                f"(detected {device_count} device(s))"
            )

        try:
            joystick = pygame.joystick.Joystick(self._binding.device)
            joystick.init()
        except Exception as exc:
            raise HotkeyRegistrationError(
                f"failed to open joystick device {self._binding.device}: {exc}"
            ) from exc

        try:
            self._binding.validate(joystick)
        except ValueError as exc:
            raise HotkeyRegistrationError(
                f"{exc} on {joystick.get_name()}"
            ) from exc

        self._joystick = joystick
        self._active = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="voice-joystick-ptt",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "joystick voice PTT active: %s (%s)",
            self._binding.format(),
            joystick.get_name(),
        )

    def stop(self) -> None:
        self._active = False
        self._stop_event.set()
        if self._thread is None:
            return

        self._thread.join(timeout=1.0)
        self._thread = None
        self._joystick = None
        self._held = False

        pygame = self._pygame_module
        if pygame is not None:
            try:
                pygame.joystick.quit()
                pygame.quit()
            except Exception:
                logger.debug("pygame shutdown after joystick listener stop failed", exc_info=True)

    def _run(self) -> None:
        joystick = self._joystick
        if joystick is None:
            return

        pygame = self._resolve_pygame()
        while self._active and not self._stop_event.is_set():
            pygame.event.pump()
            self._apply_button_state(self._binding.is_pressed(joystick))
            time.sleep(self._poll_interval_seconds)

    def _apply_button_state(self, pressed: bool) -> None:
        if pressed == self._held:
            return
        self._held = pressed
        if pressed:
            self._controller.on_press()
        else:
            self._controller.on_release()

    def _resolve_pygame(self) -> Any:
        if self._pygame_module is not None:
            return self._pygame_module

        from race_engineer.voice.hotkey.joystick_pygame import ensure_joystick_env

        ensure_joystick_env()
        import pygame

        return pygame
