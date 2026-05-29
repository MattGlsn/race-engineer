from unittest.mock import MagicMock

import pytest

from race_engineer.voice.hotkey.binding import HotkeyBinding
from race_engineer.voice.hotkey.errors import HotkeyRegistrationError
from race_engineer.voice.hotkey.listener import GlobalHotkeyListener, normalize_key


class FakeKey:
    def __init__(self, name: str, *, char: str | None = None) -> None:
        self.name = name
        self.char = char


class FakeListener:
    def __init__(self, on_press, on_release) -> None:
        self.on_press = on_press
        self.on_release = on_release

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


def test_normalize_key_maps_modifier_aliases() -> None:
    assert normalize_key(FakeKey("ctrl_r")) == "ctrl"
    assert normalize_key(FakeKey("shift_l")) == "shift"
    assert normalize_key(FakeKey("space")) == "space"
    assert normalize_key(FakeKey("a", char="A")) == "a"


def test_listener_invokes_press_and_release() -> None:
    controller = MagicMock()
    keyboard = MagicMock()
    keyboard.Listener.side_effect = lambda **kwargs: FakeListener(**kwargs)
    binding = HotkeyBinding.parse("ctrl+shift+space")
    listener = GlobalHotkeyListener(binding, controller, keyboard_module=keyboard)

    listener.start()
    listener._handle_press(FakeKey("ctrl_l"))
    listener._handle_press(FakeKey("shift_l"))
    listener._handle_press(FakeKey("space"))

    controller.on_press.assert_called_once()

    listener._handle_release(FakeKey("space"))

    controller.on_release.assert_called_once()


def test_listener_raises_when_start_fails() -> None:
    keyboard = MagicMock()

    def failing_listener(**kwargs: object) -> FakeListener:
        listener = FakeListener(**kwargs)  # type: ignore[arg-type]
        listener.start = MagicMock(side_effect=RuntimeError("access denied"))
        return listener

    keyboard.Listener.side_effect = failing_listener
    listener = GlobalHotkeyListener(
        HotkeyBinding.parse("ctrl+shift+space"),
        MagicMock(),
        keyboard_module=keyboard,
    )

    with pytest.raises(HotkeyRegistrationError, match="failed to start"):
        listener.start()
