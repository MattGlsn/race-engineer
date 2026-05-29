from typing import Any

from race_engineer.fuel import variables as var
from race_engineer.position.normalize import MAX_CARS, normalize_car_idx
from race_engineer.sdk.wrapper import IrSdkWrapper


class PlayerLapReader:
    """Reads the player's completed lap count from the iRacing SDK."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def read_laps_completed(self) -> int | None:
        """Return completed laps for the player car in one buffer snapshot."""
        if not self._sdk.is_connected:
            return None

        try:
            self._sdk.freeze_var_buffer_latest()
            car_idx = normalize_car_idx(self._read_raw(var.PLAYER_CAR_IDX))
            if car_idx is None:
                return None

            laps = self._read_int_array(var.CAR_IDX_LAP_COMPLETED)
            if laps is None or car_idx >= len(laps):
                return None

            lap_count = laps[car_idx]
            return lap_count if lap_count >= 0 else None
        finally:
            self._sdk.unfreeze_var_buffer_latest()

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
