import logging
from typing import Any

import irsdk

from race_engineer.connection.state import ConnectionState

logger = logging.getLogger(__name__)


class SdkConnectionService:
    """Manages the lifecycle of the iRacing SDK shared-memory connection."""

    def __init__(self, sdk: irsdk.IRSDK | None = None) -> None:
        self._sdk = sdk if sdk is not None else irsdk.IRSDK()
        self._state = ConnectionState.DISCONNECTED

    @property
    def state(self) -> ConnectionState:
        return self._state

    @property
    def is_connected(self) -> bool:
        return self._state == ConnectionState.CONNECTED

    def as_dict(self) -> dict[str, Any]:
        """Expose connection state for API consumers."""
        return {
            "state": self._state.value,
            "is_connected": self.is_connected,
            "sdk_initialized": bool(self._sdk.is_initialized),
            "sdk_connected": bool(self._sdk.is_connected),
        }

    def connect(self) -> bool:
        """Connect to a running iRacing simulator via the SDK."""
        if self._state == ConnectionState.CONNECTED:
            return True

        self._state = ConnectionState.CONNECTING
        logger.info("Connecting to iRacing SDK")

        try:
            started = self._sdk.startup()
        except Exception:
            logger.exception("Failed to start iRacing SDK")
            self._state = ConnectionState.DISCONNECTED
            return False

        if started and self._sdk.is_initialized and self._sdk.is_connected:
            self._state = ConnectionState.CONNECTED
            logger.info("Connected to iRacing SDK")
            return True

        logger.warning(
            "iRacing SDK startup did not connect (started=%s, initialized=%s, connected=%s)",
            started,
            self._sdk.is_initialized,
            self._sdk.is_connected,
        )
        self._state = ConnectionState.DISCONNECTED
        return False

    def _sdk_is_healthy(self) -> bool:
        return bool(self._sdk.is_initialized and self._sdk.is_connected)

    def check_health(self) -> bool:
        """Verify the SDK session is still live; reset state when connection is lost."""
        if self._state != ConnectionState.CONNECTED:
            return False

        if self._sdk_is_healthy():
            return True

        logger.warning("iRacing SDK connection lost")
        try:
            self._sdk.shutdown()
        except Exception:
            logger.exception("Error shutting down SDK after health check failure")
        self._state = ConnectionState.DISCONNECTED
        return False
