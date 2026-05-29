from unittest.mock import MagicMock

import pytest

from race_engineer.ai.llm.client import OpenAiChatClient
from race_engineer.ai.llm.config import OpenAiLlmConfig
from race_engineer.ai.llm.models import CompletionResult
from race_engineer.ai.llm.result import LlmResult
from race_engineer.ai.service import EngineerAiService
from race_engineer.context.aggregator import empty_engineer_context
from race_engineer.context.models import EngineerContext, RaceContextState, SessionContextState
from race_engineer.context.validation import validate_engineer_context


@pytest.fixture
def service() -> EngineerAiService:
    llm_client = OpenAiChatClient(
        OpenAiLlmConfig(api_key="test-key"),
        http_client=MagicMock(),
    )
    return EngineerAiService(llm_client)


def test_ask_builds_messages_from_validated_context(service: EngineerAiService) -> None:
    context = EngineerContext(
        session=SessionContextState(track_name="Spa", session_type="Race", field_size=20),
        race=RaceContextState(overall_position=3, fuel_level=42.5),
        driver=empty_engineer_context().driver,
        analytics=empty_engineer_context().analytics,
    )
    validate_engineer_context(context)

    service._llm_client.complete = MagicMock(  # type: ignore[method-assign]
        return_value=LlmResult.ok(
            CompletionResult(
                text="P3 with 42 liters.",
                model="gpt-4o-mini",
                latency_ms=120,
            )
        )
    )

    result = service.ask("What's my fuel?", context, intent="fuel")

    assert result.success is True
    assert result.data is not None
    assert result.data.text == "P3 with 42 liters."
    service._llm_client.complete.assert_called_once()
    messages = service._llm_client.complete.call_args.args[0]
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert "Spa" in messages[1]["content"]
    assert "What's my fuel?" in messages[1]["content"]
