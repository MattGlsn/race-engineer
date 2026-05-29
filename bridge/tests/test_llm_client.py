from unittest.mock import MagicMock

import httpx
import pytest

from race_engineer.ai.llm.client import OpenAiChatClient
from race_engineer.ai.llm.config import OpenAiLlmConfig
from race_engineer.ai.llm.errors import LlmErrorCode


@pytest.fixture
def config() -> OpenAiLlmConfig:
    return OpenAiLlmConfig(api_key="test-key", model="gpt-4o-mini")


def test_complete_returns_assistant_text(config: OpenAiLlmConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.return_value = httpx.Response(
        200,
        json={
            "model": "gpt-4o-mini",
            "choices": [{"message": {"role": "assistant", "content": " P3, 42 liters left. "}}],
            "usage": {"prompt_tokens": 120, "completion_tokens": 8},
        },
    )

    client = OpenAiChatClient(config, http_client=http_client)
    result = client.complete(
        [
            {"role": "system", "content": "You are the race engineer."},
            {"role": "user", "content": "What's my fuel?"},
        ]
    )

    assert result.success is True
    assert result.data is not None
    assert result.data.text == "P3, 42 liters left."
    assert result.data.model == "gpt-4o-mini"
    assert result.data.prompt_tokens == 120
    assert result.data.completion_tokens == 8
    assert result.data.latency_ms >= 0

    http_client.post.assert_called_once()
    args, kwargs = http_client.post.call_args
    assert args[0] == "https://api.openai.com/v1/chat/completions"
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"]["model"] == "gpt-4o-mini"
    assert kwargs["json"]["max_tokens"] == 150


def test_complete_rejects_empty_messages(config: OpenAiLlmConfig) -> None:
    client = OpenAiChatClient(config, http_client=MagicMock(spec=httpx.Client))

    result = client.complete([])

    assert result.success is False
    assert result.error_code == LlmErrorCode.PROVIDER_ERROR


def test_complete_maps_invalid_api_key(config: OpenAiLlmConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.return_value = httpx.Response(
        401,
        json={"error": {"message": "invalid api key"}},
    )

    client = OpenAiChatClient(config, http_client=http_client)
    result = client.complete([{"role": "user", "content": "hello"}])

    assert result.success is False
    assert result.error_code == LlmErrorCode.INVALID_API_KEY


def test_complete_maps_rate_limit(config: OpenAiLlmConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.return_value = httpx.Response(429, json={"error": {"message": "rate limit"}})

    client = OpenAiChatClient(config, http_client=http_client)
    result = client.complete([{"role": "user", "content": "hello"}])

    assert result.success is False
    assert result.error_code == LlmErrorCode.RATE_LIMIT


def test_complete_maps_server_error(config: OpenAiLlmConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.return_value = httpx.Response(503, json={"error": {"message": "unavailable"}})

    client = OpenAiChatClient(config, http_client=http_client)
    result = client.complete([{"role": "user", "content": "hello"}])

    assert result.success is False
    assert result.error_code == LlmErrorCode.PROVIDER_ERROR


def test_complete_maps_timeout(config: OpenAiLlmConfig) -> None:
    http_client = MagicMock(spec=httpx.Client)
    http_client.post.side_effect = httpx.TimeoutException("timed out")

    client = OpenAiChatClient(config, http_client=http_client)
    result = client.complete([{"role": "user", "content": "hello"}])

    assert result.success is False
    assert result.error_code == LlmErrorCode.TIMEOUT
