from __future__ import annotations

import time
from typing import Callable

from race_engineer.proactive.cooldown.models import (
    CooldownConfig,
    DEFAULT_GLOBAL_INTERVAL_SECONDS,
)
from race_engineer.proactive.cooldown.priority import (
    bypasses_global_throttle,
    sort_by_priority,
)
from race_engineer.proactive.triggers.models import TriggerEvent, TriggerType


class CooldownManager:
    """Throttles proactive trigger broadcasts to prevent message spam."""

    def __init__(
        self,
        config: CooldownConfig | None = None,
        *,
        config_provider: Callable[[], CooldownConfig] | None = None,
        global_interval_seconds: float = DEFAULT_GLOBAL_INTERVAL_SECONDS,
    ) -> None:
        if config_provider is not None:
            self._config_provider = config_provider
        else:
            resolved = config or CooldownConfig(
                global_interval_seconds=global_interval_seconds,
            )
            self._config_provider = lambda: resolved
        self._last_global_at: float | None = None
        self._last_by_type: dict[TriggerType, float] = {}
        self._session_key: str | None = None

    @property
    def config(self) -> CooldownConfig:
        return self._config_provider()

    def begin_session(self, session_key: str) -> None:
        self.reset()
        self._session_key = session_key

    def reset(self) -> None:
        self._last_global_at = None
        self._last_by_type.clear()
        self._session_key = None

    def filter(
        self,
        events: tuple[TriggerEvent, ...],
        *,
        now: float | None = None,
    ) -> tuple[TriggerEvent, ...]:
        """Return at most one highest-priority event when cooldown windows allow."""
        if not events:
            return ()

        timestamp = now if now is not None else time.monotonic()
        config = self.config

        for event in sort_by_priority(events):
            if not self._type_ready(event.type, timestamp, config):
                continue
            if not bypasses_global_throttle(event) and not self._global_ready(
                timestamp,
                config,
            ):
                continue

            self._mark_emitted(event.type, timestamp)
            return (event,)

        return ()

    def _global_ready(self, now: float, config: CooldownConfig) -> bool:
        if self._last_global_at is None:
            return True
        elapsed = now - self._last_global_at
        return elapsed >= config.global_interval_seconds

    def _type_ready(
        self,
        trigger_type: TriggerType,
        now: float,
        config: CooldownConfig,
    ) -> bool:
        last_at = self._last_by_type.get(trigger_type)
        if last_at is None:
            return True
        elapsed = now - last_at
        return elapsed >= config.interval_for(trigger_type)

    def _mark_emitted(self, trigger_type: TriggerType, now: float) -> None:
        self._last_global_at = now
        self._last_by_type[trigger_type] = now
