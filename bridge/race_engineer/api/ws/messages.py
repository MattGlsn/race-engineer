import time
from typing import Any

from race_engineer.fuel.models import FuelConsumptionSnapshot
from race_engineer.fuel.projection.models import FuelProjectionSnapshot
from race_engineer.gap.models import GapAheadSnapshot, GapBehindSnapshot
from race_engineer.position.models import PlayerPositionSnapshot
from race_engineer.session.models import Driver, Session
from race_engineer.standings.models import DriverStanding, StandingsSnapshot
from race_engineer.telemetry.models import TelemetrySnapshot


def build_connection_message(connection: dict[str, Any]) -> dict[str, Any]:
    return {"type": "connection", "ts": time.time(), "data": connection}


def build_transcript_message(
    *,
    role: str,
    text: str,
    intent: str | None = None,
    conversation_id: str | None = None,
    track_name: str | None = None,
    session_type: str | None = None,
) -> dict[str, Any]:
    data: dict[str, Any] = {"role": role, "text": text}
    if intent is not None:
        data["intent"] = intent
    if conversation_id is not None:
        data["conversation_id"] = conversation_id
    if track_name is not None:
        data["track_name"] = track_name
    if session_type is not None:
        data["session_type"] = session_type
    return {"type": "transcript", "ts": time.time(), "data": data}


def build_telemetry_message(snapshot: TelemetrySnapshot) -> dict[str, Any]:
    return {
        "type": "telemetry",
        "ts": time.time(),
        "data": _telemetry_payload(snapshot),
    }


def build_race_state_message(
    session: Session,
    standings: StandingsSnapshot,
    player_position: PlayerPositionSnapshot | None = None,
    gap_ahead: GapAheadSnapshot | None = None,
    gap_behind: GapBehindSnapshot | None = None,
    fuel_consumption: FuelConsumptionSnapshot | None = None,
    fuel_projection: FuelProjectionSnapshot | None = None,
) -> dict[str, Any]:
    return {
        "type": "race_state",
        "ts": time.time(),
        "data": {
            "session": _session_payload(session),
            "standings": _standings_payload(standings),
            "player": _player_position_payload(player_position),
            "gap_ahead": _gap_ahead_payload(gap_ahead),
            "gap_behind": _gap_behind_payload(gap_behind),
            "fuel_consumption": _fuel_consumption_payload(fuel_consumption),
            "fuel_projection": _fuel_projection_payload(fuel_projection),
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


def _player_position_payload(
    player_position: PlayerPositionSnapshot | None,
) -> dict[str, Any]:
    if player_position is None:
        return _player_position_fields(PlayerPositionSnapshot())

    return _player_position_fields(player_position)


def _player_position_fields(
    player_position: PlayerPositionSnapshot,
) -> dict[str, Any]:
    return {
        "car_idx": player_position.car_idx,
        "overall_position": player_position.overall_position,
        "class_position": player_position.class_position,
        "field_size": player_position.field_size,
    }


def _gap_ahead_payload(gap_ahead: GapAheadSnapshot | None) -> dict[str, Any]:
    if gap_ahead is None:
        return _gap_ahead_fields(GapAheadSnapshot())

    return _gap_ahead_fields(gap_ahead)


def _gap_ahead_fields(gap_ahead: GapAheadSnapshot) -> dict[str, Any]:
    return {
        "target_car_idx": gap_ahead.target_car_idx,
        "gap_seconds": gap_ahead.gap_seconds,
        "distance_meters": gap_ahead.distance_meters,
    }


def _gap_behind_payload(gap_behind: GapBehindSnapshot | None) -> dict[str, Any]:
    if gap_behind is None:
        return _gap_behind_fields(GapBehindSnapshot())

    return _gap_behind_fields(gap_behind)


def _gap_behind_fields(gap_behind: GapBehindSnapshot) -> dict[str, Any]:
    return {
        "target_car_idx": gap_behind.target_car_idx,
        "gap_seconds": gap_behind.gap_seconds,
        "distance_meters": gap_behind.distance_meters,
    }


def _fuel_consumption_payload(
    fuel_consumption: FuelConsumptionSnapshot | None,
) -> dict[str, Any]:
    if fuel_consumption is None:
        return _fuel_consumption_fields(FuelConsumptionSnapshot())

    return _fuel_consumption_fields(fuel_consumption)


def _fuel_consumption_fields(
    fuel_consumption: FuelConsumptionSnapshot,
) -> dict[str, Any]:
    return {
        "last_lap": fuel_consumption.last_lap,
        "last_lap_usage": fuel_consumption.last_lap_usage,
        "rolling_avg_usage": fuel_consumption.rolling_avg_usage,
        "valid_lap_count": fuel_consumption.valid_lap_count,
        "fuel_at_lap_start": fuel_consumption.fuel_at_lap_start,
    }


def _fuel_projection_payload(
    fuel_projection: FuelProjectionSnapshot | None,
) -> dict[str, Any]:
    if fuel_projection is None:
        return _fuel_projection_fields(FuelProjectionSnapshot())

    return _fuel_projection_fields(fuel_projection)


def _fuel_projection_fields(
    fuel_projection: FuelProjectionSnapshot,
) -> dict[str, Any]:
    return {
        "laps_remaining": fuel_projection.laps_remaining,
        "projected_finish_fuel": fuel_projection.projected_finish_fuel,
        "risk_level": fuel_projection.risk_level.value,
        "warning": fuel_projection.warning,
    }
