from typing import Any

from race_engineer.position.normalize import MAX_CARS, normalize_car_idx
from race_engineer.proactive.lap import variables as var
from race_engineer.sdk.wrapper import IrSdkWrapper


class PlayerBestLapReader:
    """Reads the player's best lap time from the iRacing SDK."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def read_best_lap_time(self) -> float | None:
        """Return best lap time for the player car in one buffer snapshot."""
        if not self._sdk.is_connected:
            return None

        try:
            self._sdk.freeze_var_buffer_latest()
            car_idx = normalize_car_idx(self._read_raw(var.PLAYER_CAR_IDX))
            if car_idx is None:
                return None

            best_laps = self._read_float_array(var.CAR_IDX_BEST_LAP_TIME)
            if best_laps is None or car_idx >= len(best_laps):
                return None

            best_lap_time = best_laps[car_idx]
            return best_lap_time if best_lap_time > 0 else None
        finally:
            self._sdk.unfreeze_var_buffer_latest()

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
