from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TelemetrySnapshot:
    """Live telemetry values read from the iRacing SDK shared-memory buffer."""

    speed: float | None = None
    fuel: float | None = None
    lap_dist_pct: float | None = None
    gear: int | None = None
    throttle: float | None = None
    brake: float | None = None
    steering: float | None = None
    rpm: float | None = None
