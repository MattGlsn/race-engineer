from typing import Any

from race_engineer.proactive.incident import variables as var
from race_engineer.sdk.wrapper import IrSdkWrapper


class IncidentReader:
    """Reads the player's incident count from the iRacing SDK."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def read_incident_count(self) -> int | None:
        """Return the player's incident count in one buffer snapshot."""
        if not self._sdk.is_connected:
            return None

        try:
            self._sdk.freeze_var_buffer_latest()
            value = self._read_raw(var.PLAYER_CAR_MY_INCIDENT_COUNT)
            if value is None:
                return None
            count = int(value)
            return count if count >= 0 else None
        finally:
            self._sdk.unfreeze_var_buffer_latest()

    def _read_raw(self, name: str) -> Any | None:
        try:
            return self._sdk.get_var(name)
        except Exception:
            return None
