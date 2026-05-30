import sqlite3

import pytest

from race_engineer.coaching.trace import TraceRecorder
from race_engineer.coaching.trace.models import TraceSample
from race_engineer.storage.database import init_schema
from race_engineer.storage.trace_repository import TraceRepository
from race_engineer.telemetry import TelemetrySnapshot


@pytest.fixture
def repository() -> TraceRepository:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_schema(connection)
    return TraceRepository(connection)


def _snapshot(
    lap_dist_pct: float = 0.1,
    *,
    speed: float = 100.0,
) -> TelemetrySnapshot:
    return TelemetrySnapshot(
        speed=speed,
        fuel=30.0,
        lap_dist_pct=lap_dist_pct,
        gear=3,
        throttle=0.8,
        brake=0.0,
        steering=0.1,
        rpm=6000.0,
    )


def test_recorder_captures_samples() -> None:
    recorder = TraceRecorder(min_samples_per_lap=1)
    recorder.begin_session("Spa|Race")

    recorder.record(_snapshot(0.1), 0, timestamp=1.0)
    recorder.record(_snapshot(0.2), 0, timestamp=2.0)

    assert recorder.current_sample_count == 2


def test_recorder_ignores_missing_lap_dist_pct() -> None:
    recorder = TraceRecorder(min_samples_per_lap=1)
    recorder.begin_session("Spa|Race")

    recorder.record(TelemetrySnapshot(speed=100.0), 0, timestamp=1.0)

    assert recorder.current_sample_count == 0


def test_recorder_segments_completed_lap(repository: TraceRepository) -> None:
    recorder = TraceRecorder(repository=repository, min_samples_per_lap=3)
    recorder.begin_session("Spa|Race")

    for index in range(3):
        recorder.record(_snapshot(index / 10), 0, timestamp=float(index))
    recorder.record(_snapshot(0.99), 1, timestamp=3.0)

    assert recorder.current_sample_count == 1
    assert repository.list_laps("Spa|Race") == [1]
    stored = repository.load("Spa|Race", 1)
    assert stored is not None
    assert stored.sample_count == 3


def test_recorder_rejects_incomplete_lap(repository: TraceRepository) -> None:
    recorder = TraceRecorder(repository=repository, min_samples_per_lap=5)
    recorder.begin_session("Spa|Race")

    for index in range(2):
        recorder.record(_snapshot(index / 10), 0, timestamp=float(index))
    recorder.record(_snapshot(0.2), 1, timestamp=2.0)

    assert repository.list_laps("Spa|Race") == []


def test_recorder_resets_on_lap_regression() -> None:
    recorder = TraceRecorder(min_samples_per_lap=1)
    recorder.begin_session("Spa|Race")

    recorder.record(_snapshot(0.5), 5, timestamp=1.0)
    recorder.record(_snapshot(0.6), 6, timestamp=2.0)
    recorder.record(_snapshot(0.1), 2, timestamp=3.0)

    assert recorder.current_sample_count == 1
