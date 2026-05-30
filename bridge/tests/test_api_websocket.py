from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.api.ws import TelemetryBroadcaster, WebSocketConnectionManager
from race_engineer.connection import SdkConnectionService
from race_engineer.session import Session
from race_engineer.position import PlayerPositionSnapshot
from race_engineer.standings import DriverStanding, StandingsSnapshot
from race_engineer.telemetry import TelemetrySnapshot


@pytest.fixture
def mock_connection_service() -> MagicMock:
    service = MagicMock(spec=SdkConnectionService)
    service.is_connected = False
    service.sdk = MagicMock()
    service.as_dict.return_value = {
        "state": "disconnected",
        "is_connected": False,
        "sdk_initialized": False,
        "sdk_connected": False,
    }
    return service


@pytest.fixture
def mock_session_reader() -> MagicMock:
    reader = MagicMock()
    reader.read.return_value = Session(
        track_name="Spa",
        session_type="Race",
    )
    return reader


@pytest.fixture
def mock_standings_reader() -> MagicMock:
    reader = MagicMock()
    reader.read_snapshot.return_value = StandingsSnapshot(
        drivers=(DriverStanding(car_idx=0, position=1, laps=5),),
    )
    return reader


@pytest.fixture
def mock_position_calculator() -> MagicMock:
    calculator = MagicMock()
    calculator.calculate.return_value = PlayerPositionSnapshot(
        car_idx=0,
        overall_position=1,
        class_position=1,
        field_size=20,
    )
    return calculator


@pytest.fixture
def mock_gap_calculator() -> MagicMock:
    from race_engineer.gap import GapAheadSnapshot

    calculator = MagicMock()
    calculator.calculate.return_value = GapAheadSnapshot()
    return calculator


@pytest.fixture
def mock_gap_behind_calculator() -> MagicMock:
    from race_engineer.gap import GapBehindSnapshot

    calculator = MagicMock()
    calculator.calculate.return_value = GapBehindSnapshot()
    return calculator


@pytest.fixture
def mock_lap_reader() -> MagicMock:
    reader = MagicMock()
    reader.read_laps_completed.return_value = 0
    return reader


@pytest.fixture
def mock_telemetry_reader() -> MagicMock:
    reader = MagicMock()
    reader.read_snapshot.return_value = TelemetrySnapshot(
        speed=42.0,
        rpm=6000.0,
        gear=3,
    )
    return reader


@pytest.fixture
def ws_manager() -> WebSocketConnectionManager:
    return WebSocketConnectionManager()


@pytest.fixture
def broadcaster(
    ws_manager: WebSocketConnectionManager,
    mock_connection_service: MagicMock,
    mock_telemetry_reader: MagicMock,
    mock_session_reader: MagicMock,
    mock_standings_reader: MagicMock,
    mock_position_calculator: MagicMock,
    mock_gap_calculator: MagicMock,
    mock_gap_behind_calculator: MagicMock,
    mock_lap_reader: MagicMock,
) -> TelemetryBroadcaster:
    return TelemetryBroadcaster(
        ws_manager,
        mock_connection_service,
        telemetry_reader=mock_telemetry_reader,
        session_reader=mock_session_reader,
        standings_reader=mock_standings_reader,
        position_calculator=mock_position_calculator,
        gap_calculator=mock_gap_calculator,
        gap_behind_calculator=mock_gap_behind_calculator,
        lap_reader=mock_lap_reader,
        telemetry_interval=0.01,
        race_state_interval=0.01,
    )


@pytest.fixture
def client(
    mock_connection_service: MagicMock,
    ws_manager: WebSocketConnectionManager,
    broadcaster: TelemetryBroadcaster,
) -> TestClient:
    app = create_app(
        connection_service=mock_connection_service,
        ws_manager=ws_manager,
        broadcaster=broadcaster,
    )
    with TestClient(app) as test_client:
        yield test_client


def test_websocket_sends_connection_message(
    client: TestClient,
    mock_connection_service: MagicMock,
) -> None:
    with client.websocket_connect("/ws") as websocket:
        message = websocket.receive_json()

    assert message["type"] == "connection"
    assert message["data"] == mock_connection_service.as_dict.return_value
    assert "ts" in message


def test_websocket_broadcasts_telemetry(
    client: TestClient,
    mock_telemetry_reader: MagicMock,
) -> None:
    with client.websocket_connect("/ws") as websocket:
        websocket.receive_json()
        telemetry = websocket.receive_json()

    assert telemetry["type"] == "telemetry"
    assert telemetry["data"]["speed"] == 42.0
    assert telemetry["data"]["rpm"] == 6000.0
    assert telemetry["data"]["gear"] == 3
    mock_telemetry_reader.read_snapshot.assert_called()


def test_websocket_disconnect_removes_client(
    client: TestClient,
    ws_manager: WebSocketConnectionManager,
) -> None:
    with client.websocket_connect("/ws") as websocket:
        assert ws_manager.client_count == 1
        websocket.receive_json()
        websocket.close()

    assert ws_manager.client_count == 0


def test_multiple_websocket_clients_receive_broadcast(
    client: TestClient,
) -> None:
    with (
        client.websocket_connect("/ws") as first,
        client.websocket_connect("/ws") as second,
    ):
        first.receive_json()
        second.receive_json()
        first_telemetry = first.receive_json()
        second_telemetry = second.receive_json()

    assert first_telemetry["type"] == "telemetry"
    assert second_telemetry["type"] == "telemetry"
    assert first_telemetry["data"]["speed"] == second_telemetry["data"]["speed"]


def _receive_until_type(websocket, message_type: str) -> dict:
    while True:
        message = websocket.receive_json()
        if message["type"] == message_type:
            return message


def test_websocket_broadcasts_connection_state_changes(
    client: TestClient,
    mock_connection_service: MagicMock,
) -> None:
    disconnected = {
        "state": "disconnected",
        "is_connected": False,
        "sdk_initialized": False,
        "sdk_connected": False,
    }
    connected = {
        "state": "connected",
        "is_connected": True,
        "sdk_initialized": True,
        "sdk_connected": True,
    }
    responses = iter([disconnected, connected])
    mock_connection_service.as_dict.side_effect = lambda: next(responses, connected)

    with client.websocket_connect("/ws") as websocket:
        first = websocket.receive_json()
        updated = _receive_until_type(websocket, "connection")

    assert first["type"] == "connection"
    assert first["data"]["state"] == "disconnected"
    assert updated["data"]["state"] == "connected"


def test_websocket_broadcasts_race_state(
    client: TestClient,
    mock_session_reader: MagicMock,
    mock_standings_reader: MagicMock,
    mock_position_calculator: MagicMock,
) -> None:
    with client.websocket_connect("/ws") as websocket:
        websocket.receive_json()
        race_state = _receive_until_type(websocket, "race_state")

    assert race_state["data"]["session"]["track_name"] == "Spa"
    assert race_state["data"]["session"]["session_type"] == "Race"
    assert race_state["data"]["standings"]["drivers"][0]["position"] == 1
    assert race_state["data"]["player"]["overall_position"] == 1
    assert race_state["data"]["player"]["class_position"] == 1
    mock_session_reader.read.assert_called()
    mock_standings_reader.read_snapshot.assert_called()
    mock_position_calculator.calculate.assert_called()
    assert race_state["data"]["gap_ahead"] == {
        "target_car_idx": None,
        "gap_seconds": None,
        "distance_meters": None,
    }
    assert race_state["data"]["gap_behind"] == {
        "target_car_idx": None,
        "gap_seconds": None,
        "distance_meters": None,
    }
    assert race_state["data"]["fuel_consumption"]["valid_lap_count"] == 0
