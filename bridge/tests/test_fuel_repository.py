import sqlite3

from race_engineer.fuel.models import LapFuelRecord
from race_engineer.storage.database import init_schema
from race_engineer.storage.fuel_repository import FuelLapRepository


def test_save_and_list_records() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_schema(connection)
    repository = FuelLapRepository(connection)

    repository.save(
        "Daytona|Race",
        LapFuelRecord(lap=1, fuel_start=30.0, fuel_end=28.5, usage_liters=1.5),
    )
    repository.save(
        "Daytona|Race",
        LapFuelRecord(lap=2, fuel_start=28.5, fuel_end=27.0, usage_liters=1.5),
    )

    records = repository.list_for_session("Daytona|Race")
    assert len(records) == 2
    assert records[0].lap == 1
    assert records[1].usage_liters == 1.5


def test_save_upserts_same_lap() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    init_schema(connection)
    repository = FuelLapRepository(connection)

    repository.save(
        "Daytona|Race",
        LapFuelRecord(lap=1, fuel_start=30.0, fuel_end=28.5, usage_liters=1.5),
    )
    repository.save(
        "Daytona|Race",
        LapFuelRecord(lap=1, fuel_start=30.0, fuel_end=28.0, usage_liters=2.0),
    )

    records = repository.list_for_session("Daytona|Race")
    assert len(records) == 1
    assert records[0].usage_liters == 2.0
