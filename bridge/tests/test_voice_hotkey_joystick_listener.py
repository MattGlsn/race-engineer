from unittest.mock import MagicMock

import pytest

from race_engineer.voice.hotkey.errors import HotkeyRegistrationError
from race_engineer.voice.hotkey.joystick_binding import JoystickBinding
from race_engineer.voice.hotkey.joystick_listener import JoystickPttListener


class FakeJoystick:
    def __init__(self, name: str = "Test Wheel", buttons: int = 20) -> None:
        self._name = name
        self._buttons = buttons

    def init(self) -> None:
        return None

    def get_name(self) -> str:
        return self._name

    def get_numbuttons(self) -> int:
        return self._buttons

    def get_button(self, button_id: int) -> bool:
        return False


def _build_fake_pygame(*, device_count: int = 1, buttons: int = 20) -> MagicMock:
    pygame = MagicMock()
    pygame.get_init.return_value = True
    pygame.joystick.get_init.return_value = True
    pygame.display.get_init.return_value = True
    pygame.display.get_surface.return_value = MagicMock()
    pygame.joystick.get_count.return_value = device_count
    pygame.joystick.Joystick.return_value = FakeJoystick(buttons=buttons)
    return pygame


def test_listener_invokes_press_and_release() -> None:
    controller = MagicMock()
    pygame = _build_fake_pygame()
    binding = JoystickBinding.parse("0:5")
    listener = JoystickPttListener(binding, controller, pygame_module=pygame)

    listener.start()
    listener._apply_button_state(True)
    listener._apply_button_state(False)
    listener.stop()

    controller.on_press.assert_called_once()
    controller.on_release.assert_called_once()


def test_listener_ignores_duplicate_state_updates() -> None:
    controller = MagicMock()
    pygame = _build_fake_pygame()
    listener = JoystickPttListener(
        JoystickBinding.parse("5"),
        controller,
        pygame_module=pygame,
    )

    listener.start()
    listener._apply_button_state(True)
    listener._apply_button_state(True)
    listener._apply_button_state(False)
    listener._apply_button_state(False)
    listener.stop()

    controller.on_press.assert_called_once()
    controller.on_release.assert_called_once()


def test_listener_raises_when_device_missing() -> None:
    pygame = _build_fake_pygame(device_count=0)
    listener = JoystickPttListener(
        JoystickBinding.parse("0:1"),
        MagicMock(),
        pygame_module=pygame,
    )

    with pytest.raises(HotkeyRegistrationError, match="device 0 not found"):
        listener.start()


def test_listener_raises_when_button_missing() -> None:
    pygame = _build_fake_pygame(buttons=3)
    listener = JoystickPttListener(
        JoystickBinding.parse("0:9"),
        MagicMock(),
        pygame_module=pygame,
    )

    with pytest.raises(HotkeyRegistrationError, match="button 9 not available"):
        listener.start()
