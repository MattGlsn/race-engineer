from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


JoystickInputKind = Literal["button", "axis"]


@dataclass(frozen=True, slots=True)
class JoystickBinding:
    """Push-to-talk steering-wheel / gamepad binding."""

    device: int
    kind: JoystickInputKind
    index: int
    axis_positive: bool = True

    @classmethod
    def parse(cls, spec: str) -> JoystickBinding:
        raw = spec.strip()
        if not raw:
            raise ValueError("joystick binding must not be empty")

        device = 0
        body = raw
        if ":" in raw:
            device_part, body = raw.split(":", maxsplit=1)
            device = _parse_non_negative_int(device_part.strip(), "device index")

        body = body.strip().lower()
        if body.startswith("axis") or body.startswith("a"):
            return cls._parse_axis(device, body)

        button = _parse_non_negative_int(body, "button index")
        return cls(device=device, kind="button", index=button)

    @classmethod
    def _parse_axis(cls, device: int, body: str) -> JoystickBinding:
        if body.startswith("axis"):
            parts = [part.strip() for part in body.split(":") if part.strip()]
            if len(parts) < 2:
                raise ValueError("axis binding must look like axis:4 or axis:4:-")
            axis = _parse_non_negative_int(parts[1], "axis index")
            axis_positive = True
            if len(parts) >= 3:
                direction = parts[2]
                if direction not in {"+", "-"}:
                    raise ValueError('axis direction must be "+" or "-"')
                axis_positive = direction == "+"
            return cls(device=device, kind="axis", index=axis, axis_positive=axis_positive)

        axis_part = body[1:]
        axis_positive = True
        if axis_part.endswith("-"):
            axis_positive = False
            axis_part = axis_part[:-1]
        elif axis_part.endswith("+"):
            axis_part = axis_part[:-1]
        axis = _parse_non_negative_int(axis_part, "axis index")
        return cls(device=device, kind="axis", index=axis, axis_positive=axis_positive)

    def format(self) -> str:
        if self.kind == "button":
            if self.device == 0:
                return str(self.index)
            return f"{self.device}:{self.index}"

        direction = "+" if self.axis_positive else "-"
        return f"{self.device}:axis:{self.index}:{direction}"

    def is_pressed(self, joystick: object) -> bool:
        if self.kind == "button":
            return bool(joystick.get_button(self.index))  # type: ignore[attr-defined]

        value = float(joystick.get_axis(self.index))  # type: ignore[attr-defined]
        if self.axis_positive:
            return value >= 0.5
        return value <= -0.5

    def validate(self, joystick: object) -> None:
        if self.kind == "button":
            button_count = joystick.get_numbuttons()  # type: ignore[attr-defined]
            if self.index >= button_count:
                raise ValueError(
                    f"button {self.index} not available "
                    f"(device has {button_count} button(s))"
                )
            return

        axis_count = joystick.get_numaxes()  # type: ignore[attr-defined]
        if self.index >= axis_count:
            raise ValueError(
                f"axis {self.index} not available (device has {axis_count} axis(es))"
            )


def _parse_non_negative_int(value: str, label: str) -> int:
    if not value:
        raise ValueError(f"joystick binding {label} must not be empty")
    try:
        parsed = int(value, 10)
    except ValueError as exc:
        raise ValueError(f"joystick binding {label} must be an integer") from exc
    if parsed < 0:
        raise ValueError(f"joystick binding {label} must be non-negative")
    return parsed
