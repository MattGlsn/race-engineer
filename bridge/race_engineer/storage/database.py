import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "race_engineer.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS fuel_lap_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_key TEXT NOT NULL,
    lap INTEGER NOT NULL,
    fuel_start REAL NOT NULL,
    fuel_end REAL NOT NULL,
    usage_liters REAL NOT NULL,
    created_at REAL NOT NULL,
    UNIQUE(session_key, lap)
);
"""


def connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a SQLite connection and ensure schema exists."""
    path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    init_schema(connection)
    return connection


def init_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(_SCHEMA)
    connection.commit()
