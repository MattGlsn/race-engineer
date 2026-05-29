from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GapAheadSnapshot:
    """Gap to the car immediately ahead on track."""

    target_car_idx: int | None = None
    gap_seconds: float | None = None
    distance_meters: float | None = None
