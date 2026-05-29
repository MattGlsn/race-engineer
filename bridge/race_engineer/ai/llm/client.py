from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from race_engineer.ai.llm.config import OpenAiLlmConfig
from race_engineer.ai.llm.errors import LlmErrorCode
from race_engineer.ai.llm.models import CompletionResult
from race_engineer.ai.llm.result import LlmResult
from race_engineer.ai.prompt.builder import ChatMessage

logger = logging.getLogger(__name__)


class OpenAiChatClient:
    """Send chat completion requests to OpenAI."""

    def __init__(
        self,
        config: OpenAiLlmConfig,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._config = config
        self._http_client = http_client
        self._owns_client = http_client is None

    def complete(
        self,
        messages: list[ChatMessage],
    ) -> LlmResult[CompletionResult]:
        if not messages:
            return LlmResult.fail(
                error_code=LlmErrorCode.PROVIDER_ERROR,
                message="messages payload is empty",
            )

        client = self._http_client or httpx.Client(
            timeout=self._config.timeout_seconds,
        )
        started = time.perf_counter()
        try:
            response = client.post(
                f"{self._config.base_url}/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self._config.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._config.model,
                    "messages": messages,
                    "max_tokens": self._config.max_completion_tokens,
                },
            )
        except httpx.TimeoutException:
            logger.exception("OpenAI chat completion timed out")
            return LlmResult.fail(
                error_code=LlmErrorCode.TIMEOUT,
                message="OpenAI chat completion timed out",
            )
        except httpx.HTTPError as exc:
            logger.exception("OpenAI chat completion network error")
            return LlmResult.fail(
                error_code=LlmErrorCode.NETWORK,
                message=str(exc),
            )
        finally:
            if self._owns_client:
                client.close()

        latency_ms = int((time.perf_counter() - started) * 1000)
        return self._parse_response(response, latency_ms=latency_ms)

    def close(self) -> None:
        if self._owns_client and self._http_client is not None:
            self._http_client.close()

    def _parse_response(
        self,
        response: httpx.Response,
        *,
        latency_ms: int,
    ) -> LlmResult[CompletionResult]:
        if response.status_code == 401:
            return LlmResult.fail(
                error_code=LlmErrorCode.INVALID_API_KEY,
                message="OpenAI rejected the API key",
            )
        if response.status_code == 429:
            return LlmResult.fail(
                error_code=LlmErrorCode.RATE_LIMIT,
                message="OpenAI rate limit exceeded",
            )
        if response.status_code >= 500:
            return LlmResult.fail(
                error_code=LlmErrorCode.PROVIDER_ERROR,
                message=f"OpenAI server error ({response.status_code})",
            )
        if response.status_code >= 400:
            detail = _response_detail(response)
            return LlmResult.fail(
                error_code=LlmErrorCode.PROVIDER_ERROR,
                message=detail or f"OpenAI request failed ({response.status_code})",
            )

        try:
            payload = response.json()
        except ValueError:
            return LlmResult.fail(
                error_code=LlmErrorCode.PROVIDER_ERROR,
                message="OpenAI returned invalid JSON",
            )

        text = _extract_assistant_text(payload)
        if text is None:
            return LlmResult.fail(
                error_code=LlmErrorCode.PROVIDER_ERROR,
                message="OpenAI response missing assistant text",
            )

        model = payload.get("model")
        if not isinstance(model, str):
            model = self._config.model

        prompt_tokens, completion_tokens = _extract_usage(payload)

        return LlmResult.ok(
            CompletionResult(
                text=text,
                model=model,
                latency_ms=latency_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
        )


def _extract_assistant_text(payload: dict[str, Any]) -> str | None:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None

    first = choices[0]
    if not isinstance(first, dict):
        return None

    message = first.get("message")
    if not isinstance(message, dict):
        return None

    content = message.get("content")
    if not isinstance(content, str):
        return None

    stripped = content.strip()
    return stripped or None


def _extract_usage(payload: dict[str, Any]) -> tuple[int | None, int | None]:
    usage = payload.get("usage")
    if not isinstance(usage, dict):
        return None, None

    prompt_tokens = usage.get("prompt_tokens")
    completion_tokens = usage.get("completion_tokens")
    prompt = prompt_tokens if isinstance(prompt_tokens, int) else None
    completion = completion_tokens if isinstance(completion_tokens, int) else None
    return prompt, completion


def _response_detail(response: httpx.Response) -> str | None:
    try:
        payload: Any = response.json()
    except ValueError:
        return None

    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str):
                return message
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
    return None
