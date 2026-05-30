from __future__ import annotations

from dataclasses import dataclass

from race_engineer.telemetry.models import TelemetrySnapshot

DEFAULT_BRAKE_ON_THRESHOLD = 0.15
DEFAULT_BRAKE_OFF_THRESHOLD = 0.08
DEFAULT_BRAKE_HOLD_SECONDS = 0.4


@dataclass(frozen=True, slots=True)
class BrakingConfig:
    on_threshold: float = DEFAULT_BRAKE_ON_THRESHOLD
    off_threshold: float = DEFAULT_BRAKE_OFF_THRESHOLD
    hold_seconds: float = DEFAULT_BRAKE_HOLD_SECONDS


class BrakingZoneTracker:
    """Tracks whether the driver is in an active braking zone with hysteresis."""

    def __init__(self, config: BrakingConfig | None = None) -> None:
        self._config = config or BrakingConfig()
        self._in_zone = False
        self._released_at: float | None = None

    @property
    def in_braking_zone(self) -> bool:
        return self._in_zone

    def update(self, snapshot: TelemetrySnapshot, *, now: float) -> bool:
        brake = snapshot.brake
        if brake is None:
            return self._in_zone

        config = self._config
        if not self._in_zone:
            if brake >= config.on_threshold:
                self._in_zone = True
                self._released_at = None
        elif brake < config.off_threshold:
            if self._released_at is None:
                self._released_at = now
            elif now - self._released_at >= config.hold_seconds:
                self._in_zone = False
                self._released_at = None
        else:
            self._released_at = None

        return self._in_zone

    def reset(self) -> None:
        self._in_zone = False
        self._released_at = None
