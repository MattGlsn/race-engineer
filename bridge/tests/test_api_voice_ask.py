from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from race_engineer.ai.llm.models import CompletionResult
from race_engineer.ai.llm.result import LlmResult
from race_engineer.ai.service import EngineerAiService
from race_engineer.api.app import create_app
from race_engineer.connection import SdkConnectionService
from race_engineer.context.aggregator import ContextAggregator, empty_engineer_context


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
def mock_engineer_ai() -> MagicMock:
    return MagicMock(spec=EngineerAiService)


@pytest.fixture
def mock_context_aggregator() -> MagicMock:
    aggregator = MagicMock(spec=ContextAggregator)
    aggregator.build.return_value = empty_engineer_context()
    return aggregator


@pytest.fixture
def client(
    mock_connection_service: MagicMock,
    mock_engineer_ai: MagicMock,
    mock_context_aggregator: MagicMock,
) -> TestClient:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        engineer_ai=mock_engineer_ai,
        context_aggregator=mock_context_aggregator,
        voice_pipeline=None,
    )
    with TestClient(app) as test_client:
        yield test_client


def test_ask_engineer_returns_success(
    client: TestClient,
    mock_engineer_ai: MagicMock,
    mock_context_aggregator: MagicMock,
) -> None:
    mock_engineer_ai.ask.return_value = LlmResult.ok(
        CompletionResult(
            text="P3, 42 liters left.",
            model="gpt-4o-mini",
            latency_ms=180,
        )
    )

    response = client.post(
        "/voice/ask",
        json={"text": "What's my fuel?", "intent": "fuel"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["text"] == "P3, 42 liters left."
    assert data["model"] == "gpt-4o-mini"
    assert data["latency_ms"] == 180
    mock_context_aggregator.build.assert_called_once()
    mock_engineer_ai.ask.assert_called_once()
    ask_args, ask_kwargs = mock_engineer_ai.ask.call_args
    assert ask_args[0] == "What's my fuel?"
    assert ask_kwargs["intent"] == "fuel"


def test_ask_engineer_unconfigured_returns_503(
    mock_connection_service: MagicMock,
    mock_context_aggregator: MagicMock,
) -> None:
    mock_connection_service.sdk = MagicMock()
    app = create_app(
        connection_service=mock_connection_service,
        engineer_ai=None,
        context_aggregator=mock_context_aggregator,
        voice_pipeline=None,
    )
    app.state.engineer_ai = None

    with TestClient(app) as client:
        response = client.post("/voice/ask", json={"text": "What's my fuel?"})

    assert response.status_code == 503
