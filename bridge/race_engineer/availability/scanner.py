from race_engineer.sdk.wrapper import IrSdkWrapper


class VariableScanner:
    """Scans the iRacing SDK for available telemetry variable names."""

    def __init__(self, sdk: IrSdkWrapper | None = None) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()

    def scan(self) -> frozenset[str]:
        """Return the set of variable names exposed by the connected SDK."""
        if not self._sdk.is_connected:
            return frozenset()

        return frozenset(self._sdk.list_variable_names())
