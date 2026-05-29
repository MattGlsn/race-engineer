import sqlite3
import time

from race_engineer.fuel.models import LapFuelRecord


class FuelLapRepository:
    """Persists per-lap fuel consumption records."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, session_key: str, record: LapFuelRecord) -> None:
        self._connection.execute(
            """
            INSERT INTO fuel_lap_records (
                session_key, lap, fuel_start, fuel_end, usage_liters, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_key, lap) DO UPDATE SET
                fuel_start = excluded.fuel_start,
                fuel_end = excluded.fuel_end,
                usage_liters = excluded.usage_liters,
                created_at = excluded.created_at
            """,
            (
                session_key,
                record.lap,
                record.fuel_start,
                record.fuel_end,
                record.usage_liters,
                time.time(),
            ),
        )
        self._connection.commit()

    def list_for_session(self, session_key: str) -> list[LapFuelRecord]:
        rows = self._connection.execute(
            """
            SELECT lap, fuel_start, fuel_end, usage_liters
            FROM fuel_lap_records
            WHERE session_key = ?
            ORDER BY lap ASC
            """,
            (session_key,),
        ).fetchall()
        return [
            LapFuelRecord(
                lap=row["lap"],
                fuel_start=row["fuel_start"],
                fuel_end=row["fuel_end"],
                usage_liters=row["usage_liters"],
            )
            for row in rows
        ]
