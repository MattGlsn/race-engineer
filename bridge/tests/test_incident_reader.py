from unittest.mock import MagicMock

from race_engineer.proactive.incident.reader import IncidentReader
from race_engineer.sdk.wrapper import IrSdkWrapper


def _mock_sdk(var_map: dict[str, object]) -> MagicMock:
    mock = MagicMock(spec=IrSdkWrapper)
    mock.is_connected = True

    def get_var(name: str) -> object:
        return var_map.get(name)

    mock.get_var.side_effect = get_var
    return mock


def test_incident_reader() -> None:
    reader = IncidentReader(
        sdk=_mock_sdk({"PlayerCarMyIncidentCount": 3}),
    )

    assert reader.read_incident_count() == 3
