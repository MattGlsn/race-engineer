import sqlite3

import pytest

from race_engineer.context.analytics import build_analytics_state
from race_engineer.context.models import AnalyticsContextState, LapFuelSummary
from race_engineer.fuel.models import FuelConsumptionSnapshot, LapFuelRecord
from race_engineer.storage.database import init_schema
from race_engineer.storage.fuel_repository import FuelLapRepository


@pytest.fixture
def repository() -> FuelLapRepository:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_schema(connection)
    return FuelLapRepository(connection)


def test_build_analytics_state(repository: FuelLapRepository) -> None:
    repository.save(
        "Spa|Race",
        LapFuelRecord(lap=1, fuel_start=30.0, fuel_end=28.0, usage_liters=2.0),
    )
    repository.save(
        "Spa|Race",
        LapFuelRecord(lap=2, fuel_start=28.0, fuel_end=26.0, usage_liters=2.0),
    )

    state = build_analytics_state(
        FuelConsumptionSnapshot(
            last_lap_usage=2.0,
            rolling_avg_usage=2.0,
            valid_lap_count=2,
        ),
        repository=repository,
        session_key="Spa|Race",
    )

    assert state == AnalyticsContextState(
        valid_lap_count=2,
        rolling_avg_usage=2.0,
        last_lap_usage=2.0,
        recent_lap_fuel=(
            LapFuelSummary(lap=1, usage_liters=2.0),
            LapFuelSummary(lap=2, usage_liters=2.0),
        ),
    )


def test_build_analytics_state_without_repository() -> None:
    state = build_analytics_state(FuelConsumptionSnapshot(valid_lap_count=0))

    assert state.recent_lap_fuel == ()
