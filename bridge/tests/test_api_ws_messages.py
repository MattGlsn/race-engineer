from race_engineer.api.ws.messages import (
    build_race_state_message,
    build_telemetry_message,
)
from race_engineer.position import PlayerPositionSnapshot
from race_engineer.session import Driver, Session
from race_engineer.standings import DriverStanding, StandingsSnapshot
from race_engineer.telemetry import TelemetrySnapshot


def test_build_telemetry_message() -> None:
    message = build_telemetry_message(
        TelemetrySnapshot(speed=10.0, gear=2),
    )

    assert message["type"] == "telemetry"
    assert message["data"]["speed"] == 10.0
    assert message["data"]["gear"] == 2
    assert "ts" in message


def test_build_race_state_message() -> None:
    message = build_race_state_message(
        Session(
            track_name="Daytona",
            session_type="Practice",
            drivers=(Driver(car_idx=0, user_name="Driver", car_number="42"),),
        ),
        StandingsSnapshot(
            drivers=(DriverStanding(car_idx=0, position=1, laps=3),),
        ),
        PlayerPositionSnapshot(
            car_idx=0,
            overall_position=1,
            class_position=1,
            field_size=20,
        ),
    )

    assert message["type"] == "race_state"
    assert message["data"]["session"]["track_name"] == "Daytona"
    assert message["data"]["session"]["drivers"][0]["car_number"] == "42"
    assert message["data"]["standings"]["drivers"][0]["laps"] == 3
    assert message["data"]["player"]["overall_position"] == 1
    assert message["data"]["player"]["class_position"] == 1
    assert message["data"]["player"]["field_size"] == 20
