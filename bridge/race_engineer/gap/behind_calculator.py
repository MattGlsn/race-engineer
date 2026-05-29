from typing import Any

from race_engineer.gap import variables as var
from race_engineer.gap.models import GapBehindSnapshot
from race_engineer.telemetry.variables import SPEED
from race_engineer.sdk.wrapper import IrSdkWrapper

MIN_SPEED_MPS = 0.1
GAP_SECONDS_PRECISION = 2


class GapBehindCalculator:
    """Calculates gap to the car behind on track from the iRacing SDK."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def calculate(self) -> GapBehindSnapshot:
        """Read gap-behind distance and interval in one SDK buffer snapshot."""
        if not self._sdk.is_connected:
            return GapBehindSnapshot()

        try:
            self._sdk.freeze_var_buffer_latest()
            distance_meters = self._read_car_dist_behind()
            gap_seconds = self._calculate_gap_seconds(distance_meters)

            return GapBehindSnapshot(
                gap_seconds=gap_seconds,
                distance_meters=distance_meters,
            )
        finally:
            self._sdk.unfreeze_var_buffer_latest()

    def _read_car_dist_behind(self) -> float | None:
        value = self._read_raw(var.CAR_DIST_BEHIND)
        if value is None:
            return None

        try:
            distance = float(value)
        except (TypeError, ValueError):
            return None

        return distance if distance > 0 else None

    def _calculate_gap_seconds(self, distance_meters: float | None) -> float | None:
        if distance_meters is None:
            return None

        speed = self._read_speed_mps()
        if speed is None:
            return None

        gap_seconds = distance_meters / speed
        return round(gap_seconds, GAP_SECONDS_PRECISION)

    def _read_speed_mps(self) -> float | None:
        value = self._read_raw(SPEED)
        if value is None:
            return None

        try:
            speed = float(value)
        except (TypeError, ValueError):
            return None

        return speed if speed >= MIN_SPEED_MPS else None

    def _read_raw(self, name: str) -> Any | None:
        try:
            return self._sdk.get_var(name)
        except Exception:
            return None
