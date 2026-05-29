from typing import Any

from race_engineer.position import variables as var
from race_engineer.position.models import PlayerPositionSnapshot
from race_engineer.position.normalize import (
    MAX_CARS,
    count_active_positions,
    empty_snapshot,
    normalize_car_idx,
    normalize_positive_int,
)
from race_engineer.sdk.wrapper import IrSdkWrapper


class PositionCalculator:
    """Calculates the player's live race position from the iRacing SDK."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def calculate(self) -> PlayerPositionSnapshot:
        """Read and normalize the player's position in one SDK buffer snapshot."""
        if not self._sdk.is_connected:
            return empty_snapshot()

        try:
            self._sdk.freeze_var_buffer_latest()
            car_idx = self._read_player_car_idx()
            if car_idx is None:
                return empty_snapshot()

            positions = self._read_int_array(var.CAR_IDX_POSITION)
            if positions is None:
                return empty_snapshot()

            return PlayerPositionSnapshot(
                car_idx=car_idx,
                overall_position=self._read_overall_position(positions, car_idx),
                class_position=self._read_class_position(car_idx),
                field_size=count_active_positions(positions),
            )
        finally:
            self._sdk.unfreeze_var_buffer_latest()

    def _read_player_car_idx(self) -> int | None:
        return normalize_car_idx(self._read_raw(var.PLAYER_CAR_IDX))

    def _read_overall_position(
        self,
        positions: list[int],
        car_idx: int,
    ) -> int | None:
        if car_idx >= len(positions):
            return None

        return normalize_positive_int(positions[car_idx])

    def _read_class_position(self, car_idx: int) -> int | None:
        class_positions = self._read_int_array(var.CAR_IDX_CLASS_POSITION)
        if class_positions is None or car_idx >= len(class_positions):
            return None

        return normalize_positive_int(class_positions[car_idx])

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

    def _read_raw(self, name: str) -> Any | None:
        try:
            return self._sdk.get_var(name)
        except Exception:
            return None
