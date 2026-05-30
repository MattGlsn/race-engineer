from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Sector:
    """One distance slice of a lap."""

    index: int
    start_dist_pct: float
    end_dist_pct: float
    avg_speed: float | None = None
    duration_seconds: float | None = None


@dataclass(frozen=True, slots=True)
class LapSectors:
    """Fixed-width sector breakdown for one completed lap."""

    lap: int
    sectors: tuple[Sector, ...]
