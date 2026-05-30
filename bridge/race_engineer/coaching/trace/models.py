from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TraceSample:
    """One telemetry sample captured during a lap."""

    timestamp: float
    lap_dist_pct: float
    speed: float
    fuel: float
    gear: int
    throttle: float
    brake: float
    steering: float
    rpm: float


@dataclass(frozen=True, slots=True)
class LapTrace:
    """All samples recorded for one completed lap."""

    lap: int
    samples: tuple[TraceSample, ...]


@dataclass(frozen=True, slots=True)
class CompressedLapTrace:
    """Zlib-compressed lap trace ready for persistence."""

    lap: int
    sample_count: int
    data: bytes
