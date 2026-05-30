from __future__ import annotations

import os
from typing import Any


def ensure_joystick_env() -> None:
    """Allow wheel input while another app (e.g. iRacing) has focus."""
    os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")


def init_pygame_joystick(pygame: Any) -> None:
    """Initialize pygame so joystick events and polling work on Windows."""
    ensure_joystick_env()

    if not pygame.get_init():
        pygame.init()
    if not pygame.joystick.get_init():
        pygame.joystick.init()

    if not pygame.display.get_init():
        pygame.display.init()
    if pygame.display.get_surface() is None:
        hidden = getattr(pygame, "HIDDEN", 0)
        try:
            pygame.display.set_mode((1, 1), flags=hidden)
        except TypeError:
            pygame.display.set_mode((1, 1))
