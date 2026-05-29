from typing import Any

from race_engineer.fuel.projection import variables as var
from race_engineer.fuel.projection.laps import normalize_laps_remaining
from race_engineer.sdk.wrapper import IrSdkWrapper


class SessionLapsReader:
    """Reads session laps remaining from the iRacing SDK."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def read_laps_remaining(self) -> int | None:
        """Return laps left in the session, or None when unavailable."""
        if not self._sdk.is_connected:
            return None

        try:
            self._sdk.freeze_var_buffer_latest()
            return normalize_laps_remaining(self._read_raw(var.SESSION_LAPS_REMAIN_EX))
        finally:
            self._sdk.unfreeze_var_buffer_latest()

    def _read_raw(self, name: str) -> Any | None:
        try:
            return self._sdk.get_var(name)
        except Exception:
            return None
