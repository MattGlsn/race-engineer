from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.api.app import create_app
from race_engineer.connection import SdkConnectionService


@pytest.fixture
def mock_connection_service() -> MagicMock:
    service = MagicMock(spec=SdkConnectionService)
    service.is_connected = False
    service.as_dict.return_value = {
        "state": "disconnected",
        "is_connected": False,
        "sdk_initialized": False,
        "sdk_connected": False,
    }
    return service


@pytest.fixture
def client(mock_connection_service: MagicMock) -> TestClient:
    mock_connection_service.sdk = MagicMock()
    app = create_app(connection_service=mock_connection_service)
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client: TestClient, mock_connection_service: MagicMock) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["connection"]["state"] == "disconnected"
    mock_connection_service.as_dict.assert_called_once()
    mock_connection_service.check_health.assert_not_called()


def test_health_endpoint_checks_sdk_when_connected(
    client: TestClient, mock_connection_service: MagicMock
) -> None:
    mock_connection_service.is_connected = True
    mock_connection_service.check_health.return_value = True

    response = client.get("/health")

    assert response.status_code == 200
    mock_connection_service.check_health.assert_called_once()


def test_openapi_docs_available(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200


def test_cors_allows_localhost_origin(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_lifecycle_disconnects_on_shutdown(mock_connection_service: MagicMock) -> None:
    app = create_app(connection_service=mock_connection_service)

    with TestClient(app):
        pass

    mock_connection_service.disconnect.assert_called_once()
