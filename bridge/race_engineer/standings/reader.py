from typing import Any

from race_engineer.sdk.wrapper import IrSdkWrapper
from race_engineer.standings import variables as var
from race_engineer.standings.models import DriverStanding, StandingsSnapshot

MAX_CARS = 64


class StandingsReader:
    """Reads live race standings from the iRacing SDK shared-memory buffer."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def read_snapshot(self) -> StandingsSnapshot:
        """Read standings variables in one consistent buffer snapshot."""
        if not self._sdk.is_connected:
            return StandingsSnapshot()

        try:
            self._sdk.freeze_var_buffer_latest()
            positions = self._read_int_array(var.CAR_IDX_POSITION)
            if positions is None:
                return StandingsSnapshot()

            drivers = [
                DriverStanding(car_idx=car_idx, position=position)
                for car_idx, position in enumerate(positions[:MAX_CARS])
                if position > 0
            ]
            drivers.sort(key=lambda driver: driver.position)
            return StandingsSnapshot(drivers=tuple(drivers))
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
