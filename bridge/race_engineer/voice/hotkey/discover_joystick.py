"""Print steering-wheel button IDs for configuring VOICE_JOYSTICK_PTT."""

from __future__ import annotations

import time
from typing import Any

from race_engineer.voice.hotkey.joystick_pygame import ensure_joystick_env, init_pygame_joystick

_POLL_INTERVAL_SECONDS = 0.01
_AXIS_THRESHOLD = 0.5


def _open_devices(pygame: Any) -> list[Any]:
    devices: list[Any] = []
    for index in range(pygame.joystick.get_count()):
        device = pygame.joystick.Joystick(index)
        device.init()
        devices.append(device)
    return devices


def _describe_device(index: int, device: Any) -> str:
    return (
        f"Device {index}: {device.get_name()} | "
        f"buttons={device.get_numbuttons()} "
        f"axes={device.get_numaxes()} "
        f"hats={device.get_numhats()}"
    )


def _print_devices(devices: list[Any]) -> None:
    print(f"Joysticks found: {len(devices)}", flush=True)
    for index, device in enumerate(devices):
        print(_describe_device(index, device), flush=True)
    print(
        "Press wheel buttons/paddles (Ctrl+C to exit)...",
        flush=True,
    )
    print(
        "If nothing appears, your wheel may be on another device index, "
        "reporting axes instead of buttons, or locked by iRacing.",
        flush=True,
    )
    print(
        "Use device:button or device:axis:N for VOICE_JOYSTICK_PTT "
        '(example: "1:12" or "0:axis:4").',
        flush=True,
    )


def main() -> None:
    ensure_joystick_env()
    import pygame

    init_pygame_joystick(pygame)

    devices = _open_devices(pygame)
    if not devices:
        print("No joysticks detected. Connect your wheel and run again.", flush=True)
        return

    _print_devices(devices)

    previous_buttons = [
        [False] * device.get_numbuttons() for device in devices
    ]
    previous_axes = [
        [0.0] * device.get_numaxes() for device in devices
    ]
    previous_hats = [
        [(0, 0)] * device.get_numhats() for device in devices
    ]

    try:
        while True:
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    print(
                        f"[device={event.joy}] Pressed button ID: {event.button}",
                        flush=True,
                    )
                elif event.type == pygame.JOYBUTTONUP:
                    print(
                        f"[device={event.joy}] Released button ID: {event.button}",
                        flush=True,
                    )
                elif event.type == pygame.JOYAXISMOTION:
                    value = float(event.value)
                    if abs(value) >= _AXIS_THRESHOLD:
                        print(
                            f"[device={event.joy}] Axis {event.axis} moved: {value:+.2f}",
                            flush=True,
                        )
                elif event.type == pygame.JOYHATMOTION:
                    if event.value != (0, 0):
                        print(
                            f"[device={event.joy}] Hat {event.hat} moved: {event.value}",
                            flush=True,
                        )

            for device_index, device in enumerate(devices):
                for button_id in range(device.get_numbuttons()):
                    pressed = bool(device.get_button(button_id))
                    if pressed and not previous_buttons[device_index][button_id]:
                        print(
                            f"[device={device_index}] Pressed button ID: {button_id}",
                            flush=True,
                        )
                    elif not pressed and previous_buttons[device_index][button_id]:
                        print(
                            f"[device={device_index}] Released button ID: {button_id}",
                            flush=True,
                        )
                    previous_buttons[device_index][button_id] = pressed

                for axis_id in range(device.get_numaxes()):
                    value = float(device.get_axis(axis_id))
                    previous = previous_axes[device_index][axis_id]
                    if abs(value) >= _AXIS_THRESHOLD and (
                        abs(previous) < _AXIS_THRESHOLD
                        or (previous >= 0) != (value >= 0)
                    ):
                        print(
                            f"[device={device_index}] Axis {axis_id} active: {value:+.2f}",
                            flush=True,
                        )
                    previous_axes[device_index][axis_id] = value

                for hat_id in range(device.get_numhats()):
                    value = device.get_hat(hat_id)
                    if value != previous_hats[device_index][hat_id]:
                        if value != (0, 0):
                            print(
                                f"[device={device_index}] Hat {hat_id} moved: {value}",
                                flush=True,
                            )
                        previous_hats[device_index][hat_id] = value

            time.sleep(_POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)


if __name__ == "__main__":
    main()
