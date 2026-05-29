import pytest

from race_engineer.voice.hotkey.binding import HotkeyBinding


def test_parse_ctrl_shift_space() -> None:
    binding = HotkeyBinding.parse("ctrl+shift+space")

    assert binding.modifiers == frozenset({"ctrl", "shift"})
    assert binding.key == "space"


def test_matches_requires_modifiers_and_key() -> None:
    binding = HotkeyBinding.parse("ctrl+shift+space")

    assert binding.matches(frozenset({"ctrl", "shift", "space"}))
    assert not binding.matches(frozenset({"ctrl", "space"}))
    assert not binding.matches(frozenset({"ctrl", "shift"}))


def test_parse_rejects_multiple_trigger_keys() -> None:
    with pytest.raises(ValueError, match="exactly one non-modifier"):
        HotkeyBinding.parse("ctrl+a+b")
