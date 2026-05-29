from pathlib import Path
from unittest.mock import MagicMock

import pytest

from race_engineer.session import Driver, Session, SessionInfoReader
from race_engineer.session.yaml_loader import load_session_yaml

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_YAML = (FIXTURES_DIR / "sample_session.yaml").read_text(encoding="utf-8")
SAMPLE_DATA = load_session_yaml(SAMPLE_YAML)


@pytest.fixture
def mock_sdk() -> MagicMock:
    sdk = MagicMock()
    sdk.is_initialized = False
    sdk.is_connected = False
    sdk.get_var.return_value = None
    sdk.get_session_info_yaml.return_value = None
    sdk.get_session_info.return_value = None
    return sdk


def test_read_disconnected_returns_empty_session(mock_sdk: MagicMock) -> None:
    reader = SessionInfoReader(sdk=mock_sdk)

    session = reader.read()

    assert session == Session()
    mock_sdk.get_session_info_yaml.assert_not_called()


def test_read_from_session_info_yaml(mock_sdk: MagicMock) -> None:
    mock_sdk.is_initialized = True
    mock_sdk.is_connected = True
    mock_sdk.get_var.return_value = 0
    mock_sdk.get_session_info_yaml.return_value = SAMPLE_YAML
    reader = SessionInfoReader(sdk=mock_sdk)

    session = reader.read()

    assert session.track_name == "Lucas Oil Raceway"
    assert session.session_type == "Practice"
    assert len(session.drivers) == 2
    assert session.drivers[0].user_name == "Driver One"


def test_read_from_session_info_sections(mock_sdk: MagicMock) -> None:
    mock_sdk.is_initialized = True
    mock_sdk.is_connected = True
    mock_sdk.get_var.return_value = 1

    def get_session_info(key: str):
        return SAMPLE_DATA.get(key)

    mock_sdk.get_session_info.side_effect = get_session_info
    reader = SessionInfoReader(sdk=mock_sdk)

    session = reader.read()

    assert session.track_name == "Lucas Oil Raceway"
    assert session.session_type == "Race"
    assert session.drivers == (
        Driver(
            car_idx=0,
            user_name="Driver One",
            car_number="42",
            car_class_id=0,
            car_class_short_name="MX-5",
        ),
        Driver(
            car_idx=1,
            user_name="Driver Two",
            car_number="7",
            car_class_id=1,
            car_class_short_name="GT3",
        ),
    )
