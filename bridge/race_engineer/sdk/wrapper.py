from typing import Any, Protocol

import irsdk


class IrSdkClient(Protocol):
    @property
    def is_initialized(self) -> bool: ...

    @property
    def is_connected(self) -> bool: ...

    def startup(self) -> bool: ...

    def shutdown(self) -> None: ...

    def freeze_var_buffer_latest(self) -> None: ...

    def unfreeze_var_buffer_latest(self) -> None: ...

    @property
    def var_headers_names(self) -> list[str]: ...

    def __getitem__(self, key: str) -> Any: ...


class IrSdkWrapper:
    """Thin wrapper around pyirsdk for dependency injection and testing."""

    def __init__(self, sdk: IrSdkClient | None = None) -> None:
        self._sdk: IrSdkClient = sdk if sdk is not None else irsdk.IRSDK()

    @property
    def is_initialized(self) -> bool:
        return bool(self._sdk.is_initialized)

    @property
    def is_connected(self) -> bool:
        return bool(self._sdk.is_connected)

    def startup(self) -> bool:
        return bool(self._sdk.startup())

    def shutdown(self) -> None:
        self._sdk.shutdown()

    def freeze_var_buffer_latest(self) -> None:
        self._sdk.freeze_var_buffer_latest()

    def unfreeze_var_buffer_latest(self) -> None:
        self._sdk.unfreeze_var_buffer_latest()

    def get_var(self, name: str) -> Any | None:
        try:
            return self._sdk[name]
        except (KeyError, TypeError):
            return None

    def list_variable_names(self) -> list[str]:
        """Return SDK telemetry variable names when connected."""
        if not self.is_connected:
            return []

        try:
            return list(self._sdk.var_headers_names)
        except Exception:
            return []
