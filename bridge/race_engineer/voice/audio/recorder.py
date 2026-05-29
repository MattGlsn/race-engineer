from __future__ import annotations

import os
from typing import Any

from race_engineer.voice.audio.models import (
    DEFAULT_CHANNELS,
    DEFAULT_SAMPLE_RATE,
    AudioBuffer,
)


class RecordingError(Exception):
    """Raised when start/stop recording is invoked in an invalid state."""


def resolve_input_settings(
    sd: Any,
    *,
    sample_rate: int,
    channels: int,
) -> tuple[int, int]:
    """Pick a PortAudio input device and sample rate that can open a stream."""
    env_device = _parse_voice_input_device_env()
    if env_device is not None:
        return _resolve_device_settings(
            sd,
            env_device,
            sample_rate=sample_rate,
            channels=channels,
            env_override=True,
        )

    input_devices = _list_input_devices(sd)
    if not input_devices:
        raise RecordingError("no microphone input device available")

    candidates = _input_device_candidates(sd, input_devices)
    for device_index in candidates:
        try:
            return _resolve_device_settings(
                sd,
                device_index,
                sample_rate=sample_rate,
                channels=channels,
            )
        except RecordingError:
            continue

    names = ", ".join(str(device.get("name", device_index)) for device_index, device in input_devices)
    raise RecordingError(
        f"no microphone supports {sample_rate} Hz recording; available inputs: {names}"
    )


def _resolve_device_settings(
    sd: Any,
    device_index: int,
    *,
    sample_rate: int,
    channels: int,
    env_override: bool = False,
) -> tuple[int, int]:
    if not _device_has_input(sd, device_index):
        if env_override:
            raise RecordingError(
                f"VOICE_INPUT_DEVICE {device_index} is not a valid input device"
            )
        raise RecordingError(f"audio input device {device_index} is not available")

    device_info = _query_device_info(sd, device_index)
    for rate in _candidate_sample_rates(device_info, sample_rate):
        if _device_accepts_settings(
            sd,
            device_index,
            sample_rate=rate,
            channels=channels,
        ):
            return device_index, rate

    raise RecordingError(
        f"audio input device {device_index} does not support {sample_rate} Hz recording"
    )


def _list_input_devices(sd: Any) -> list[tuple[int, dict[str, Any]]]:
    try:
        devices = sd.query_devices()
    except Exception as exc:
        raise RecordingError("no microphone input device available") from exc

    if isinstance(devices, dict):
        devices = [devices]

    input_devices: list[tuple[int, dict[str, Any]]] = []
    for device in devices:
        if int(device.get("max_input_channels", 0)) <= 0:
            continue
        index = int(device.get("index", len(input_devices)))
        input_devices.append((index, device))

    input_devices.sort(key=lambda item: (_device_preference(item[1]), item[0]))
    return input_devices


def _input_device_candidates(
    sd: Any,
    input_devices: list[tuple[int, dict[str, Any]]],
) -> list[int]:
    candidates: list[int] = []

    try:
        default_in, _ = sd.default.device
    except (TypeError, ValueError, AttributeError):
        default_in = None

    if isinstance(default_in, int) and default_in >= 0 and _device_has_input(sd, default_in):
        candidates.append(default_in)

    for device_index, _ in input_devices:
        candidates.append(device_index)

    seen: set[int] = set()
    ordered: list[int] = []
    for device_index in candidates:
        if device_index in seen:
            continue
        seen.add(device_index)
        ordered.append(device_index)
    return ordered


def _device_preference(device: dict[str, Any]) -> int:
    name = str(device.get("name", "")).lower()
    if "microphone" in name or name.startswith("mic "):
        return 0
    if "stereo mix" in name or "loopback" in name:
        return 2
    return 1


def _candidate_sample_rates(device: dict[str, Any], preferred: int) -> list[int]:
    rates = [preferred]
    default_rate = device.get("default_samplerate")
    if default_rate is not None:
        rates.append(int(default_rate))
    for rate in (48_000, 44_100):
        if rate not in rates:
            rates.append(rate)
    return rates


def _query_device_info(sd: Any, index: int) -> dict[str, Any]:
    info = sd.query_devices(index)
    if isinstance(info, dict):
        return info
    return {"index": index}


def _device_accepts_settings(
    sd: Any,
    index: int,
    *,
    sample_rate: int,
    channels: int,
) -> bool:
    try:
        sd.check_input_settings(
            device=index,
            samplerate=sample_rate,
            channels=channels,
            dtype="int16",
        )
        return True
    except Exception:
        return False


def _parse_voice_input_device_env() -> int | None:
    raw = os.environ.get("VOICE_INPUT_DEVICE")
    if raw is None:
        return None

    try:
        return int(raw)
    except ValueError as exc:
        raise RecordingError("VOICE_INPUT_DEVICE must be an integer") from exc


def _device_has_input(sd: Any, index: int) -> bool:
    try:
        info = sd.query_devices(index)
    except Exception:
        return False

    return int(info.get("max_input_channels", 0)) > 0


class AudioRecorder:
    """Captures microphone input into an in-memory PCM buffer."""

    def __init__(
        self,
        *,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        channels: int = DEFAULT_CHANNELS,
        sd: Any | None = None,
    ) -> None:
        self._sample_rate = sample_rate
        self._channels = channels
        self._sd = sd
        self._stream: Any | None = None
        self._chunks: list[bytes] = []
        self._recording_sample_rate: int | None = None

    @property
    def is_recording(self) -> bool:
        return self._stream is not None

    def start(self) -> None:
        if self._stream is not None:
            raise RecordingError("recording already in progress")

        sd = self._resolve_sounddevice()
        self._chunks = []

        def callback(indata: bytes, frames: int, time_info: Any, status: Any) -> None:
            del frames, time_info, status
            self._chunks.append(bytes(indata))

        try:
            device, sample_rate = resolve_input_settings(
                sd,
                sample_rate=self._sample_rate,
                channels=self._channels,
            )
            self._recording_sample_rate = sample_rate
            self._stream = sd.RawInputStream(
                samplerate=sample_rate,
                channels=self._channels,
                dtype="int16",
                device=device,
                callback=callback,
            )
            self._stream.start()
        except RecordingError:
            raise
        except Exception as exc:
            raise RecordingError(str(exc)) from exc

    def stop(self) -> AudioBuffer:
        if self._stream is None:
            raise RecordingError("recording is not in progress")

        self._stream.stop()
        self._stream.close()
        self._stream = None

        sample_rate = self._recording_sample_rate or self._sample_rate
        self._recording_sample_rate = None

        return AudioBuffer(
            pcm_bytes=b"".join(self._chunks),
            sample_rate=sample_rate,
            channels=self._channels,
        )

    def _resolve_sounddevice(self) -> Any:
        if self._sd is not None:
            return self._sd

        import sounddevice as sd_module

        return sd_module
