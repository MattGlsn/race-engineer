from __future__ import annotations

import time

from race_engineer.proactive.cooldown.models import CooldownConfig, DEFAULT_GLOBAL_INTERVAL_SECONDS
from race_engineer.proactive.triggers.models import TriggerEvent


class CooldownManager:
    """Throttles proactive trigger broadcasts to prevent message spam."""

    def __init__(
        self,
        config: CooldownConfig | None = None,
        *,
        global_interval_seconds: float = DEFAULT_GLOBAL_INTERVAL_SECONDS,
    ) -> None:
        self._config = config or CooldownConfig(
            global_interval_seconds=global_interval_seconds,
        )
        self._last_global_at: float | None = None
        self._session_key: str | None = None

    @property
    def config(self) -> CooldownConfig:
        return self._config

    def begin_session(self, session_key: str) -> None:
        self.reset()
        self._session_key = session_key

    def reset(self) -> None:
        self._last_global_at = None
        self._session_key = None

    def filter(
        self,
        events: tuple[TriggerEvent, ...],
        *,
        now: float | None = None,
    ) -> tuple[TriggerEvent, ...]:
        """Return at most one event when the global throttle window allows."""
        if not events:
            return ()

        timestamp = now if now is not None else time.monotonic()
        if not self._global_ready(timestamp):
            return ()

        self._last_global_at = timestamp
        return (events[0],)

    def _global_ready(self, now: float) -> bool:
        if self._last_global_at is None:
            return True
        elapsed = now - self._last_global_at
        return elapsed >= self._config.global_interval_seconds
