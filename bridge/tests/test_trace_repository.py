import sqlite3

import pytest

from race_engineer.coaching.trace.compress import compress_lap_trace
from race_engineer.coaching.trace.models import LapTrace, TraceSample
from race_engineer.storage.database import init_schema
from race_engineer.storage.trace_repository import TraceRepository


@pytest.fixture
def repository() -> TraceRepository:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_schema(connection)
    return TraceRepository(connection)


def _compressed(lap: int, sample_count: int) -> object:
    samples = tuple(
        TraceSample(
            timestamp=float(index),
            lap_dist_pct=index / 100.0,
            speed=100.0,
            fuel=30.0,
            gear=3,
            throttle=0.8,
            brake=0.0,
            steering=0.0,
            rpm=6000.0,
        )
        for index in range(sample_count)
    )
    return compress_lap_trace(LapTrace(lap=lap, samples=samples))


def test_repository_save_and_load(repository: TraceRepository) -> None:
    trace = _compressed(1, 4)
    repository.save("Spa|Race", trace)

    loaded = repository.load("Spa|Race", 1)
    assert loaded is not None
    assert loaded.lap == 1
    assert loaded.sample_count == 4
    assert loaded.data == trace.data


def test_repository_lists_laps_in_order(repository: TraceRepository) -> None:
    repository.save("Spa|Race", _compressed(1, 2))
    repository.save("Spa|Race", _compressed(3, 2))
    repository.save("Spa|Race", _compressed(2, 2))

    assert repository.list_laps("Spa|Race") == [1, 2, 3]


def test_repository_prunes_old_laps(repository: TraceRepository) -> None:
    for lap in range(1, 8):
        repository.save("Spa|Race", _compressed(lap, 2))

    repository.prune_old_laps("Spa|Race", 3)

    assert repository.list_laps("Spa|Race") == [5, 6, 7]
