from pathlib import Path

from race_engineer.session.yaml_loader import load_session_yaml

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_load_session_yaml_parses_fixture() -> None:
    text = (FIXTURES_DIR / "sample_session.yaml").read_text(encoding="utf-8")

    data = load_session_yaml(text)

    assert data["WeekendInfo"]["TrackDisplayName"] == "Lucas Oil Raceway"
    assert len(data["DriverInfo"]["Drivers"]) == 2


def test_load_empty_yaml_returns_empty_dict() -> None:
    assert load_session_yaml("") == {}
    assert load_session_yaml("   ") == {}


def test_load_invalid_yaml_returns_empty_dict() -> None:
    assert load_session_yaml(":\n  bad: [") == {}
