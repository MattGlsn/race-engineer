from __future__ import annotations

from dataclasses import dataclass

MODIFIER_NAMES = frozenset({"ctrl", "shift", "alt", "cmd", "win"})


@dataclass(frozen=True, slots=True)
class HotkeyBinding:
    """Normalized push-to-talk key combination."""

    modifiers: frozenset[str]
    key: str

    @classmethod
    def parse(cls, spec: str) -> HotkeyBinding:
        parts = [part.strip().lower() for part in spec.split("+") if part.strip()]
        if not parts:
            raise ValueError("hotkey binding must include at least one key")

        modifiers = frozenset(part for part in parts if part in MODIFIER_NAMES)
        keys = [part for part in parts if part not in MODIFIER_NAMES]
        if len(keys) != 1:
            raise ValueError("hotkey binding must include exactly one non-modifier key")

        return cls(modifiers=modifiers, key=keys[0])

    def matches(self, pressed: frozenset[str]) -> bool:
        return self.modifiers <= pressed and self.key in pressed

    def is_trigger_release(self, released: str, still_pressed: frozenset[str]) -> bool:
        if released != self.key:
            return False
        remaining = still_pressed - {released}
        return self.modifiers <= remaining
