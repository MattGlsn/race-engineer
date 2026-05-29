import time
from typing import Any

from race_engineer.session.models import Driver, Session
from race_engineer.standings.models import DriverStanding, StandingsSnapshot
from race_engineer.telemetry.models import TelemetrySnapshot


def build_connection_message(connection: dict[str, Any]) -> dict[str, Any]:
    return {"type": "connection", "ts": time.time(), "data": connection}


def build_telemetry_message(snapshot: TelemetrySnapshot) -> dict[str, Any]:
    return {
        "type": "telemetry",
        "ts": time.time(),
        "data": _telemetry_payload(snapshot),
    }


def build_race_state_message(
    session: Session,
    standings: StandingsSnapshot,
) -> dict[str, Any]:
    return {
        "type": "race_state",
        "ts": time.time(),
        "data": {
            "session": _session_payload(session),
            "standings": _standings_payload(standings),
        },
    }


def _telemetry_payload(snapshot: TelemetrySnapshot) -> dict[str, Any]:
    return {
        "speed": snapshot.speed,
        "fuel": snapshot.fuel,
        "lap_dist_pct": snapshot.lap_dist_pct,
        "gear": snapshot.gear,
        "throttle": snapshot.throttle,
        "brake": snapshot.brake,
        "steering": snapshot.steering,
        "rpm": snapshot.rpm,
    }


def _session_payload(session: Session) -> dict[str, Any]:
    return {
        "track_name": session.track_name,
        "session_type": session.session_type,
        "drivers": [_driver_payload(driver) for driver in session.drivers],
    }


def _driver_payload(driver: Driver) -> dict[str, Any]:
    return {
        "car_idx": driver.car_idx,
        "user_name": driver.user_name,
        "car_number": driver.car_number,
        "car_class_id": driver.car_class_id,
        "car_class_short_name": driver.car_class_short_name,
    }


def _standings_payload(standings: StandingsSnapshot) -> dict[str, Any]:
    return {
        "drivers": [_standing_payload(driver) for driver in standings.drivers],
    }


def _standing_payload(driver: DriverStanding) -> dict[str, Any]:
    return {
        "car_idx": driver.car_idx,
        "position": driver.position,
        "laps": driver.laps,
        "class_position": driver.class_position,
        "class_id": driver.class_id,
        "best_lap_time": driver.best_lap_time,
    }
