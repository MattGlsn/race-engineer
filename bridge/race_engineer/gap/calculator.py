from race_engineer.gap.models import GapAheadSnapshot
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
            return GapAheadSnapshot()
        finally:
            self._sdk.unfreeze_var_buffer_latest()
