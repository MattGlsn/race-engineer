from __future__ import annotations

import time
from collections import deque

from race_engineer.proactive.cooldown.priority import bypasses_global_throttle
from race_engineer.proactive.suppression.models import SuppressionConfig
from race_engineer.proactive.suppression.workload import WorkloadMonitor
from race_engineer.proactive.triggers.models import TriggerEvent


class SpeechSuppressionManager:
    """Defers proactive triggers and engineer speech during high driver workload."""

    def __init__(
        self,
        workload_monitor: WorkloadMonitor,
        config: SuppressionConfig | None = None,
    ) -> None:
        self._workload = workload_monitor
        self._config = config or SuppressionConfig()
        self._pending_triggers: deque[tuple[TriggerEvent, float]] = deque()

    def reset(self) -> None:
        self._pending_triggers.clear()

    def accept_trigger(
        self,
        event: TriggerEvent,
        *,
        now: float | None = None,
    ) -> tuple[TriggerEvent, ...]:
        """Return events to broadcast now; queue non-urgent events while suppressed."""
        timestamp = now if now is not None else time.monotonic()
        self._expire_old(timestamp)

        if bypasses_global_throttle(event) or not self._workload.should_suppress():
            return (event,)

        self._enqueue_trigger(event, timestamp)
        return ()

    def drain_triggers(
        self,
        *,
        now: float | None = None,
        max_release: int = 1,
    ) -> tuple[TriggerEvent, ...]:
        """Release deferred triggers when workload has dropped."""
        if self._workload.should_suppress() or max_release <= 0:
            return ()

        timestamp = now if now is not None else time.monotonic()
        self._expire_old(timestamp)

        released: list[TriggerEvent] = []
        while self._pending_triggers and len(released) < max_release:
            event, _ = self._pending_triggers.popleft()
            released.append(event)
        return tuple(released)

    def _enqueue_trigger(self, event: TriggerEvent, now: float) -> None:
        self._pending_triggers.append((event, now))
        while len(self._pending_triggers) > self._config.max_pending_triggers:
            self._pending_triggers.popleft()

    def _expire_old(self, now: float) -> None:
        max_age = self._config.max_pending_age_seconds
        while self._pending_triggers:
            _, enqueued_at = self._pending_triggers[0]
            if now - enqueued_at <= max_age:
                break
            self._pending_triggers.popleft()
