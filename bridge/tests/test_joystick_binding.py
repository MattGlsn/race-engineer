import pytest

from race_engineer.voice.hotkey.joystick_binding import JoystickBinding


def test_parse_button_only_defaults_device_zero() -> None:
    binding = JoystickBinding.parse("12")
    assert binding.device == 0
    assert binding.kind == "button"
    assert binding.index == 12
    assert binding.format() == "12"


def test_parse_device_and_button() -> None:
    binding = JoystickBinding.parse("1:7")
    assert binding.device == 1
    assert binding.kind == "button"
    assert binding.index == 7
    assert binding.format() == "1:7"


def test_parse_axis_binding() -> None:
    binding = JoystickBinding.parse("0:axis:4:-")
    assert binding.device == 0
    assert binding.kind == "axis"
    assert binding.index == 4
    assert binding.axis_positive is False
    assert binding.format() == "0:axis:4:-"


def test_parse_short_axis_binding() -> None:
    binding = JoystickBinding.parse("2:a5+")
    assert binding.device == 2
    assert binding.kind == "axis"
    assert binding.index == 5
    assert binding.axis_positive is True


def test_is_pressed_for_button() -> None:
    class FakeJoystick:
        def get_button(self, index: int) -> bool:
            return index == 3

    binding = JoystickBinding.parse("3")
    assert binding.is_pressed(FakeJoystick()) is True
    assert JoystickBinding.parse("4").is_pressed(FakeJoystick()) is False


def test_is_pressed_for_axis() -> None:
    class FakeJoystick:
        def __init__(self, value: float) -> None:
            self._value = value

        def get_axis(self, index: int) -> float:
            return self._value

    positive = JoystickBinding.parse("0:axis:2")
    negative = JoystickBinding.parse("0:axis:2:-")

    assert positive.is_pressed(FakeJoystick(0.9)) is True
    assert positive.is_pressed(FakeJoystick(-0.9)) is False
    assert negative.is_pressed(FakeJoystick(-0.9)) is True


def test_parse_rejects_invalid_values() -> None:
    with pytest.raises(ValueError, match="must be an integer"):
        JoystickBinding.parse("abc")

    with pytest.raises(ValueError, match="must be non-negative"):
        JoystickBinding.parse("-1")

    with pytest.raises(ValueError, match="must not be empty"):
        JoystickBinding.parse("")
