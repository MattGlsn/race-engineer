from unittest.mock import MagicMock

import pytest

from race_engineer.availability import VariableScanner


@pytest.fixture
def mock_sdk() -> MagicMock:
    sdk = MagicMock()
    sdk.is_initialized = False
    sdk.is_connected = False
    sdk.list_variable_names.return_value = []
    return sdk


def test_scan_disconnected_returns_empty(mock_sdk: MagicMock) -> None:
    scanner = VariableScanner(sdk=mock_sdk)

    available = scanner.scan()

    assert available == frozenset()
    mock_sdk.list_variable_names.assert_not_called()


def test_scan_connected_returns_variable_names(mock_sdk: MagicMock) -> None:
    mock_sdk.is_initialized = True
    mock_sdk.is_connected = True
    mock_sdk.list_variable_names.return_value = ["Speed", "RPM", "Gear"]
    scanner = VariableScanner(sdk=mock_sdk)

    available = scanner.scan()

    assert available == frozenset({"Speed", "RPM", "Gear"})
    mock_sdk.list_variable_names.assert_called_once()


def test_scan_deduplicates_variable_names(mock_sdk: MagicMock) -> None:
    mock_sdk.is_initialized = True
    mock_sdk.is_connected = True
    mock_sdk.list_variable_names.return_value = ["Speed", "Speed", "RPM"]
    scanner = VariableScanner(sdk=mock_sdk)

    available = scanner.scan()

    assert available == frozenset({"Speed", "RPM"})
