from pathlib import Path

from race_engineer.session.models import Driver, Session
from race_engineer.session.parser import parse_session
from race_engineer.session.yaml_loader import load_session_yaml

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_session_from_fixture() -> None:
    text = (FIXTURES_DIR / "sample_session.yaml").read_text(encoding="utf-8")
    data = load_session_yaml(text)

    session = parse_session(data, session_num=0)

    assert session == Session(
        track_name="Lucas Oil Raceway",
        session_type="Practice",
        drivers=(
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
        ),
    )


def test_parse_session_race_type() -> None:
    text = (FIXTURES_DIR / "sample_session.yaml").read_text(encoding="utf-8")
    data = load_session_yaml(text)

    session = parse_session(data, session_num=1)

    assert session.session_type == "Race"


def test_parse_empty_data_returns_empty_session() -> None:
    session = parse_session({})

    assert session == Session()
