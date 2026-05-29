"""iRacing SDK variable names for on-track gap fields."""

from race_engineer.position.variables import CAR_IDX_POSITION, PLAYER_CAR_IDX

CAR_DIST_AHEAD = "CarDistAhead"
CAR_DIST_BEHIND = "CarDistBehind"
CAR_IDX_LAP_COMPLETED = "CarIdxLapCompleted"
CAR_IDX_LAP_DIST_PCT = "CarIdxLapDistPct"

__all__ = [
    "CAR_DIST_AHEAD",
    "CAR_DIST_BEHIND",
    "CAR_IDX_LAP_COMPLETED",
    "CAR_IDX_LAP_DIST_PCT",
    "CAR_IDX_POSITION",
    "PLAYER_CAR_IDX",
]
