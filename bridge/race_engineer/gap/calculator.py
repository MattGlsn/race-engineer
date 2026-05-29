from typing import Any

from race_engineer.gap import variables as var
from race_engineer.gap.models import GapAheadSnapshot
from race_engineer.position.normalize import MAX_CARS, normalize_car_idx, normalize_positive_int
from race_engineer.sdk.wrapper import IrSdkWrapper


class GapAheadCalculator:
    """Calculates gap to the car ahead on track from the iRacing SDK."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def calculate(self) -> GapAheadSnapshot:
        """Read gap-ahead fields in one SDK buffer snapshot."""
        if not self._sdk.is_connected:
            return GapAheadSnapshot()

        try:
            self._sdk.freeze_var_buffer_latest()
            player_car_idx = normalize_car_idx(self._read_raw(var.PLAYER_CAR_IDX))
            if player_car_idx is None:
                return GapAheadSnapshot()

            target_car_idx = self._find_target_car_idx(player_car_idx)
            if target_car_idx is None:
                return GapAheadSnapshot()

            return GapAheadSnapshot(target_car_idx=target_car_idx)
        finally:
            self._sdk.unfreeze_var_buffer_latest()

    def _find_target_car_idx(self, player_car_idx: int) -> int | None:
        """Return the car index immediately ahead on track, if any."""
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

            delta = car_track_pos - player_track_pos
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
        if player_position is None or player_position <= 1:
            return None

        target_position = player_position - 1
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
