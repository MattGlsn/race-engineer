from __future__ import annotations

import time
from dataclasses import dataclass, field

from race_engineer.proactive.suppression.braking import BrakingConfig, BrakingZoneTracker
from race_engineer.telemetry.models import TelemetrySnapshot

DEFAULT_MIN_SPEED_MPS = 5.0
DEFAULT_STEERING_BUSY_RAD = 0.35
DEFAULT_STEERING_RATE_RAD_PER_S = 1.2


@dataclass(frozen=True, slots=True)
class WorkloadConfig:
    min_speed_mps: float = DEFAULT_MIN_SPEED_MPS
    steering_busy_rad: float = DEFAULT_STEERING_BUSY_RAD
    steering_rate_rad_per_s: float = DEFAULT_STEERING_RATE_RAD_PER_S
    braking: BrakingConfig = field(default_factory=BrakingConfig)


class WorkloadMonitor:
    """Detects high driver workload from live telemetry."""

    def __init__(self, config: WorkloadConfig | None = None) -> None:
        self._config = config or WorkloadConfig()
        self._braking = BrakingZoneTracker(self._config.braking)
        self._prev_steering: float | None = None
        self._prev_at: float | None = None
        self._high_workload = False

    @property
    def in_braking_zone(self) -> bool:
        return self._braking.in_braking_zone

    @property
    def is_high_workload(self) -> bool:
        return self._high_workload

    def should_suppress(self) -> bool:
        return self._high_workload

    def observe(
        self,
        snapshot: TelemetrySnapshot,
        *,
        now: float | None = None,
    ) -> bool:
        timestamp = now if now is not None else time.monotonic()
        braking = self._braking.update(snapshot, now=timestamp)

        speed = snapshot.speed
        if speed is None or speed < self._config.min_speed_mps:
            self._high_workload = False
            self._prev_steering = snapshot.steering
            self._prev_at = timestamp
            return self._high_workload

        steering = snapshot.steering
        high_steering = (
            steering is not None
            and abs(steering) >= self._config.steering_busy_rad
        )

        high_rate = False
        if (
            steering is not None
            and self._prev_steering is not None
            and self._prev_at is not None
        ):
            elapsed = timestamp - self._prev_at
            if elapsed > 0:
                rate = abs(steering - self._prev_steering) / elapsed
                high_rate = rate >= self._config.steering_rate_rad_per_s

        self._high_workload = braking or high_steering or high_rate
        self._prev_steering = steering
        self._prev_at = timestamp
        return self._high_workload

    def reset(self) -> None:
        self._braking.reset()
        self._prev_steering = None
        self._prev_at = None
        self._high_workload = False
