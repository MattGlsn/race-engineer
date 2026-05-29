from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Driver:
    """Driver entry from iRacing SessionInfo DriverInfo."""

    car_idx: int
    user_name: str
    car_number: str
    car_class_id: int | None = None
    car_class_short_name: str | None = None
