from typing import Any

from race_engineer.session.models import Driver, Session


def parse_session(data: dict[str, Any], session_num: int = 0) -> Session:
    """Build a Session from parsed iRacing session YAML data."""
    weekend_info = data.get("WeekendInfo")
    session_info = data.get("SessionInfo")
    driver_info = data.get("DriverInfo")

    return Session(
        track_name=_parse_track_name(weekend_info),
        session_type=_parse_session_type(session_info, session_num),
        drivers=_parse_drivers(driver_info),
    )


def _parse_track_name(weekend_info: Any) -> str | None:
    if not isinstance(weekend_info, dict):
        return None

    track_display_name = weekend_info.get("TrackDisplayName")
    if isinstance(track_display_name, str) and track_display_name:
        return track_display_name

    track_name = weekend_info.get("TrackName")
    if isinstance(track_name, str) and track_name:
        return track_name

    return None


def _parse_session_type(session_info: Any, session_num: int) -> str | None:
    if not isinstance(session_info, dict):
        return None

    sessions = session_info.get("Sessions")
    if not isinstance(sessions, list):
        return None

    for entry in sessions:
        if not isinstance(entry, dict):
            continue
        if entry.get("SessionNum") == session_num:
            session_type = entry.get("SessionType")
            return str(session_type) if session_type is not None else None

    return None


def _parse_drivers(driver_info: Any) -> tuple[Driver, ...]:
    if not isinstance(driver_info, dict):
        return ()

    drivers = driver_info.get("Drivers")
    if not isinstance(drivers, list):
        return ()

    parsed: list[Driver] = []
    for entry in drivers:
        driver = _parse_driver(entry)
        if driver is not None:
            parsed.append(driver)

    return tuple(parsed)


def _parse_driver(entry: Any) -> Driver | None:
    if not isinstance(entry, dict):
        return None

    car_idx = entry.get("CarIdx")
    user_name = entry.get("UserName")
    if car_idx is None or user_name is None:
        return None

    car_number = entry.get("CarNumber", "")
    return Driver(
        car_idx=int(car_idx),
        user_name=str(user_name),
        car_number=str(car_number),
        car_class_id=_optional_int(entry.get("CarClassID")),
        car_class_short_name=_optional_str(entry.get("CarClassShortName")),
    )


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
