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

    def get_session_info(self, key: str) -> Any | None:
        """Return a parsed session info section from the SDK."""
        if not self.is_connected:
            return None

        try:
            return self._sdk[key]
        except (KeyError, TypeError):
            return None

    def get_session_info_yaml(self) -> str | None:
        """Return the raw session info YAML string from shared memory."""
        if not self.is_connected:
            return None

        try:
            header = getattr(self._sdk, "_header", None)
            shared_mem = getattr(self._sdk, "_shared_mem", None)
            if header is None or shared_mem is None:
                return None

            raw = shared_mem[
                header.session_info_offset : header.session_info_offset
                + header.session_info_len
            ]
            return raw.rstrip(b"\x00").decode("cp1252")
        except Exception:
            return None
