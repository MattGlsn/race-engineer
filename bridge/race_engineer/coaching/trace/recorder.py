import time
from typing import TYPE_CHECKING

from race_engineer.coaching.trace.compress import compress_lap_trace
from race_engineer.coaching.trace.models import LapTrace, TraceSample
from race_engineer.telemetry.models import TelemetrySnapshot

if TYPE_CHECKING:
    from race_engineer.storage.trace_repository import TraceRepository

DEFAULT_MIN_SAMPLES_PER_LAP = 50
DEFAULT_RETAINED_LAP_LIMIT = 5


class TraceRecorder:
    """Captures telemetry samples, segments by lap, and stores compressed traces."""

    def __init__(
        self,
        repository: "TraceRepository | None" = None,
        *,
        min_samples_per_lap: int = DEFAULT_MIN_SAMPLES_PER_LAP,
        retained_lap_limit: int = DEFAULT_RETAINED_LAP_LIMIT,
    ) -> None:
        self._repository = repository
        self._min_samples_per_lap = min_samples_per_lap
        self._retained_lap_limit = retained_lap_limit
        self._session_key: str | None = None
        self._last_lap_completed: int | None = None
        self._current_samples: list[TraceSample] = []

    @property
    def session_key(self) -> str | None:
        return self._session_key

    @property
    def current_sample_count(self) -> int:
        return len(self._current_samples)

    def begin_session(self, session_key: str) -> None:
        self.reset()
        self._session_key = session_key

    def reset(self) -> None:
        self._session_key = None
        self._last_lap_completed = None
        self._current_samples = []

    def record(
        self,
        snapshot: TelemetrySnapshot,
        laps_completed: int | None,
        *,
        timestamp: float | None = None,
    ) -> None:
        if self._session_key is None:
            return
        if laps_completed is None or laps_completed < 0:
            return
        if snapshot.lap_dist_pct is None:
            return

        if (
            self._last_lap_completed is not None
            and laps_completed < self._last_lap_completed
        ):
            self._last_lap_completed = laps_completed
            self._current_samples = []

        if self._last_lap_completed is None:
            self._last_lap_completed = laps_completed

        if laps_completed > self._last_lap_completed:
            self._finalize_current_lap(laps_completed)

        sample_timestamp = timestamp if timestamp is not None else time.monotonic()
        self._current_samples.append(
            self._sample_from_snapshot(snapshot, sample_timestamp)
        )

    def _finalize_current_lap(self, laps_completed: int) -> None:
        if len(self._current_samples) >= self._min_samples_per_lap:
            lap_trace = LapTrace(
                lap=laps_completed,
                samples=tuple(self._current_samples),
            )
            if self._repository is not None and self._session_key is not None:
                compressed = compress_lap_trace(lap_trace)
                self._repository.save(self._session_key, compressed)
                self._repository.prune_old_laps(
                    self._session_key,
                    self._retained_lap_limit,
                )

        self._last_lap_completed = laps_completed
        self._current_samples = []

    @staticmethod
    def _sample_from_snapshot(
        snapshot: TelemetrySnapshot,
        timestamp: float,
    ) -> TraceSample:
        return TraceSample(
            timestamp=timestamp,
            lap_dist_pct=snapshot.lap_dist_pct or 0.0,
            speed=snapshot.speed or 0.0,
            fuel=snapshot.fuel or 0.0,
            gear=snapshot.gear or 0,
            throttle=snapshot.throttle or 0.0,
            brake=snapshot.brake or 0.0,
            steering=snapshot.steering or 0.0,
            rpm=snapshot.rpm or 0.0,
        )
