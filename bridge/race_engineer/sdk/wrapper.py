from typing import Protocol

import irsdk


class IrSdkClient(Protocol):
    @property
    def is_initialized(self) -> bool: ...

    @property
    def is_connected(self) -> bool: ...

    def startup(self) -> bool: ...

    def shutdown(self) -> None: ...


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
