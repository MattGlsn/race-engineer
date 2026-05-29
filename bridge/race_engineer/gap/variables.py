"""iRacing SDK variable names for gap-ahead fields."""

from race_engineer.position.variables import CAR_IDX_POSITION, PLAYER_CAR_IDX
from race_engineer.telemetry.variables import SPEED

CAR_DIST_AHEAD = "CarDistAhead"
CAR_IDX_LAP_COMPLETED = "CarIdxLapCompleted"
CAR_IDX_LAP_DIST_PCT = "CarIdxLapDistPct"

__all__ = [
    "CAR_DIST_AHEAD",
    "CAR_IDX_LAP_COMPLETED",
    "CAR_IDX_LAP_DIST_PCT",
    "CAR_IDX_POSITION",
    "PLAYER_CAR_IDX",
    "SPEED",
]
