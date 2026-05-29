from typing import Any

from race_engineer.sdk.wrapper import IrSdkWrapper
from race_engineer.telemetry import variables as var
from race_engineer.telemetry.models import TelemetrySnapshot


class TelemetryVariableReader:
    """Reads live telemetry variables from the iRacing SDK shared-memory buffer."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def read_snapshot(self) -> TelemetrySnapshot:
        """Read all configured telemetry variables in one consistent buffer snapshot."""
        if not self._sdk.is_connected:
            return TelemetrySnapshot()

        try:
            self._sdk.freeze_var_buffer_latest()
            return TelemetrySnapshot(
                speed=self._read_float(var.SPEED),
                fuel=self._read_float(var.FUEL_LEVEL),
                lap_dist_pct=self._read_float(var.LAP_DIST_PCT),
                gear=self._read_int(var.GEAR),
                throttle=self._read_float(var.THROTTLE),
                brake=self._read_float(var.BRAKE),
                steering=self._read_float(var.STEERING_WHEEL_ANGLE),
                rpm=self._read_float(var.RPM),
            )
        finally:
            self._sdk.unfreeze_var_buffer_latest()

    def _read_float(self, name: str) -> float | None:
        value = self._read_raw(name)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _read_int(self, name: str) -> int | None:
        value = self._read_raw(name)
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _read_raw(self, name: str) -> Any | None:
        try:
            return self._sdk.get_var(name)
        except Exception:
            return None
