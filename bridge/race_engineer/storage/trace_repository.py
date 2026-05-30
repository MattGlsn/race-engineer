import sqlite3
import threading
import time

from race_engineer.coaching.trace.models import CompressedLapTrace


class TraceRepository:
    """Persists compressed lap traces."""

    def __init__(
        self,
        connection: sqlite3.Connection,
        *,
        lock: threading.Lock | None = None,
    ) -> None:
        self._connection = connection
        self._lock = lock or threading.Lock()

    def save(self, session_key: str, trace: CompressedLapTrace) -> None:
        with self._lock:
            self._connection.execute(
                """
                INSERT INTO lap_traces (
                    session_key, lap, sample_count, compressed_data, created_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_key, lap) DO UPDATE SET
                    sample_count = excluded.sample_count,
                    compressed_data = excluded.compressed_data,
                    created_at = excluded.created_at
                """,
                (
                    session_key,
                    trace.lap,
                    trace.sample_count,
                    trace.data,
                    time.time(),
                ),
            )
            self._connection.commit()

    def load(self, session_key: str, lap: int) -> CompressedLapTrace | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT lap, sample_count, compressed_data
                FROM lap_traces
                WHERE session_key = ? AND lap = ?
                """,
                (session_key, lap),
            ).fetchone()
        if row is None:
            return None
        return CompressedLapTrace(
            lap=row["lap"],
            sample_count=row["sample_count"],
            data=bytes(row["compressed_data"]),
        )

    def list_laps(self, session_key: str) -> list[int]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT lap
                FROM lap_traces
                WHERE session_key = ?
                ORDER BY lap ASC
                """,
                (session_key,),
            ).fetchall()
        return [row["lap"] for row in rows]

    def prune_old_laps(self, session_key: str, limit: int) -> None:
        if limit <= 0:
            return
        with self._lock:
            self._connection.execute(
                """
                DELETE FROM lap_traces
                WHERE session_key = ?
                  AND lap NOT IN (
                      SELECT lap
                      FROM lap_traces
                      WHERE session_key = ?
                      ORDER BY lap DESC
                      LIMIT ?
                  )
                """,
                (session_key, session_key, limit),
            )
            self._connection.commit()
