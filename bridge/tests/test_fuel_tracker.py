import sqlite3

import pytest

from race_engineer.fuel.models import LapFuelRecord
from race_engineer.fuel.tracker import FuelConsumptionTracker, build_session_key
from race_engineer.storage.database import init_schema
from race_engineer.storage.fuel_repository import FuelLapRepository


@pytest.fixture
def repository() -> FuelLapRepository:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_schema(connection)
    return FuelLapRepository(connection)


def test_build_session_key() -> None:
    assert build_session_key("Daytona", "Race") == "Daytona|Race"
    assert build_session_key(None, None) == "unknown|unknown"


def test_tracker_records_lap_on_increment(repository: FuelLapRepository) -> None:
    tracker = FuelConsumptionTracker(repository=repository)
    tracker.begin_session("Daytona|Practice")

    tracker.update(30.0, 0)
    snapshot = tracker.update(28.5, 1)

    assert snapshot.last_lap == 1
    assert snapshot.last_lap_usage == 1.5
    assert snapshot.fuel_at_lap_start == 28.5
    records = repository.list_for_session("Daytona|Practice")
    assert records == [
        LapFuelRecord(lap=1, fuel_start=30.0, fuel_end=28.5, usage_liters=1.5),
    ]


def test_tracker_ignores_invalid_usage(repository: FuelLapRepository) -> None:
    tracker = FuelConsumptionTracker(repository=repository)
    tracker.begin_session("Daytona|Practice")

    tracker.update(10.0, 0)
    snapshot = tracker.update(12.0, 1)

    assert snapshot.last_lap == 1
    assert snapshot.last_lap_usage is None
    assert repository.list_for_session("Daytona|Practice") == []


def test_tracker_rejects_spike_lap(repository: FuelLapRepository) -> None:
    tracker = FuelConsumptionTracker(repository=repository)
    tracker.begin_session("Daytona|Practice")

    tracker.update(30.0, 0)
    tracker.update(28.5, 1)
    tracker.update(27.0, 2)
    snapshot = tracker.update(10.0, 3)

    assert snapshot.valid_lap_count == 2
    assert snapshot.last_lap_usage == 1.5
    assert len(repository.list_for_session("Daytona|Practice")) == 2


def test_tracker_resets_on_lap_regression() -> None:
    tracker = FuelConsumptionTracker()
    tracker.begin_session("Daytona|Practice")

    tracker.update(30.0, 5)
    tracker.update(28.0, 6)
    snapshot = tracker.update(29.0, 2)

    assert snapshot.valid_lap_count == 0
    assert snapshot.fuel_at_lap_start == 29.0
