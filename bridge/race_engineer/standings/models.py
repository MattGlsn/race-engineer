from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DriverStanding:
    """Race standing for one car index in the current session."""

    car_idx: int
    position: int


@dataclass(frozen=True, slots=True)
class StandingsSnapshot:
    """Live standings read from the iRacing SDK shared-memory buffer."""

    drivers: tuple[DriverStanding, ...] = ()
