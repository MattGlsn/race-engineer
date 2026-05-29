from typing import Any

from race_engineer.gap import variables as var
from race_engineer.gap.models import GapBehindSnapshot
from race_engineer.telemetry.variables import SPEED
from race_engineer.position.normalize import MAX_CARS, normalize_car_idx, normalize_positive_int
from race_engineer.sdk.wrapper import IrSdkWrapper

MIN_SPEED_MPS = 0.1
GAP_SECONDS_PRECISION = 2


class GapBehindCalculator:
    """Calculates gap to the car behind on track from the iRacing SDK."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def calculate(self) -> GapBehindSnapshot:
        """Read gap-behind fields in one SDK buffer snapshot."""
        if not self._sdk.is_connected:
            return GapBehindSnapshot()

        try:
            self._sdk.freeze_var_buffer_latest()
            player_car_idx = normalize_car_idx(self._read_raw(var.PLAYER_CAR_IDX))
            if player_car_idx is None:
                return GapBehindSnapshot()

            target_car_idx = self._find_target_car_idx(player_car_idx)
            if target_car_idx is None:
                return GapBehindSnapshot()

            distance_meters = self._read_car_dist_behind()
            gap_seconds = self._calculate_gap_seconds(distance_meters)

            return GapBehindSnapshot(
                target_car_idx=target_car_idx,
                gap_seconds=gap_seconds,
                distance_meters=distance_meters,
            )
        finally:
            self._sdk.unfreeze_var_buffer_latest()

    def _find_target_car_idx(self, player_car_idx: int) -> int | None:
        """Return the car index immediately behind on track, if any."""
        target = self._find_target_by_track_position(player_car_idx)
        if target is not None:
            return target

        return self._find_target_by_classification(player_car_idx)

    def _find_target_by_track_position(self, player_car_idx: int) -> int | None:
        lap_completed = self._read_int_array(var.CAR_IDX_LAP_COMPLETED)
        lap_dist_pct = self._read_float_array(var.CAR_IDX_LAP_DIST_PCT)
        positions = self._read_int_array(var.CAR_IDX_POSITION)
        if lap_completed is None or lap_dist_pct is None or positions is None:
            return None

        player_track_pos = self._track_position(
            lap_completed,
            lap_dist_pct,
            player_car_idx,
        )
        if player_track_pos is None:
            return None

        target_car_idx: int | None = None
        smallest_delta: float | None = None
        for car_idx in range(MAX_CARS):
            if car_idx == player_car_idx or positions[car_idx] <= 0:
                continue

            car_track_pos = self._track_position(lap_completed, lap_dist_pct, car_idx)
            if car_track_pos is None:
                continue

            delta = player_track_pos - car_track_pos
            if delta <= 0:
                continue

            if smallest_delta is None or delta < smallest_delta:
                smallest_delta = delta
                target_car_idx = car_idx

        return target_car_idx

    def _find_target_by_classification(self, player_car_idx: int) -> int | None:
        positions = self._read_int_array(var.CAR_IDX_POSITION)
        if positions is None or player_car_idx >= len(positions):
            return None

        player_position = normalize_positive_int(positions[player_car_idx])
        if player_position is None:
            return None

        target_position = player_position + 1
        for car_idx, position in enumerate(positions[:MAX_CARS]):
            if normalize_positive_int(position) == target_position:
                return car_idx

        return None

    @staticmethod
    def _track_position(
        lap_completed: list[int],
        lap_dist_pct: list[float],
        car_idx: int,
    ) -> float | None:
        if car_idx >= len(lap_completed) or car_idx >= len(lap_dist_pct):
            return None

        laps = lap_completed[car_idx]
        if laps < 0:
            return None

        lap_fraction = lap_dist_pct[car_idx]
        if lap_fraction < 0:
            return None

        return laps + lap_fraction

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

    def _read_int_array(self, name: str) -> list[int] | None:
        value = self._read_raw(name)
        if value is None:
            return None
        if not isinstance(value, list):
            return None

        result: list[int] = []
        for item in value[:MAX_CARS]:
            try:
                result.append(int(item))
            except (TypeError, ValueError):
                result.append(0)
        return result

    def _read_float_array(self, name: str) -> list[float] | None:
        value = self._read_raw(name)
        if value is None:
            return None
        if not isinstance(value, list):
            return None

        result: list[float] = []
        for item in value[:MAX_CARS]:
            try:
                result.append(float(item))
            except (TypeError, ValueError):
                result.append(0.0)
        return result

    def _read_raw(self, name: str) -> Any | None:
        try:
            return self._sdk.get_var(name)
        except Exception:
            return None
