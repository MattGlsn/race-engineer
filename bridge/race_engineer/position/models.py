from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayerPositionSnapshot:
    """Normalized player race position from the iRacing SDK."""

    car_idx: int | None = None
    overall_position: int | None = None
    class_position: int | None = None
    field_size: int | None = None
