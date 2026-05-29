import logging
import time
from typing import Any

from race_engineer.availability.checker import VariableAvailabilityChecker
from race_engineer.availability.models import VariableAvailabilityReport
from race_engineer.availability.report import log_report
from race_engineer.availability.scanner import VariableScanner
from race_engineer.connection.state import ConnectionState
from race_engineer.sdk.wrapper import IrSdkWrapper

logger = logging.getLogger(__name__)

DEFAULT_RECONNECT_ATTEMPTS = 5
DEFAULT_RECONNECT_DELAY_SECONDS = 1.0


class SdkConnectionService:
    """Manages the lifecycle of the iRacing SDK shared-memory connection."""

    def __init__(
        self,
        sdk: IrSdkWrapper | None = None,
        reconnect_attempts: int = DEFAULT_RECONNECT_ATTEMPTS,
        reconnect_delay_seconds: float = DEFAULT_RECONNECT_DELAY_SECONDS,
    ) -> None:
        self._sdk = sdk if sdk is not None else IrSdkWrapper()
        self._reconnect_attempts = reconnect_attempts
        self._reconnect_delay_seconds = reconnect_delay_seconds
        self._state = ConnectionState.DISCONNECTED

    @property
    def state(self) -> ConnectionState:
        return self._state

    @property
    def is_connected(self) -> bool:
        return self._state == ConnectionState.CONNECTED

    @property
    def sdk(self) -> IrSdkWrapper:
        return self._sdk

    def as_dict(self) -> dict[str, Any]:
        """Expose connection state for API consumers."""
        return {
            "state": self._state.value,
            "is_connected": self.is_connected,
            "sdk_initialized": self._sdk.is_initialized,
            "sdk_connected": self._sdk.is_connected,
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
            self._check_variable_availability()
            return True

        logger.warning(
            "iRacing SDK startup did not connect (started=%s, initialized=%s, connected=%s)",
            started,
            self._sdk.is_initialized,
            self._sdk.is_connected,
        )
        self._state = ConnectionState.DISCONNECTED
        return False

    def disconnect(self) -> None:
        """Release the SDK shared-memory connection."""
        if self._state == ConnectionState.DISCONNECTED:
            return

        logger.info("Disconnecting from iRacing SDK")
        try:
            self._sdk.shutdown()
        except Exception:
            logger.exception("Error shutting down iRacing SDK")
        self._state = ConnectionState.DISCONNECTED

    def reconnect(self) -> bool:
        """Attempt to re-establish the SDK connection after a simulator restart."""
        self._state = ConnectionState.RECONNECTING
        logger.info("Attempting to reconnect to iRacing SDK")

        for attempt in range(1, self._reconnect_attempts + 1):
            try:
                self._sdk.shutdown()
            except Exception:
                logger.exception("Error shutting down SDK before reconnect attempt")

            if self.connect():
                logger.info("Reconnected to iRacing SDK on attempt %s", attempt)
                return True

            logger.warning(
                "Reconnect attempt %s/%s failed",
                attempt,
                self._reconnect_attempts,
            )
            if attempt < self._reconnect_attempts:
                time.sleep(self._reconnect_delay_seconds)

        self._state = ConnectionState.DISCONNECTED
        logger.error(
            "Failed to reconnect to iRacing SDK after %s attempts",
            self._reconnect_attempts,
        )
        return False

    def _sdk_is_healthy(self) -> bool:
        return self._sdk.is_initialized and self._sdk.is_connected

    def _check_variable_availability(self) -> VariableAvailabilityReport:
        scanner = VariableScanner(sdk=self._sdk)
        checker = VariableAvailabilityChecker()
        report = checker.check(scanner.scan())
        log_report(report)
        return report

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
