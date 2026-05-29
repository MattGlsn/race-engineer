from race_engineer.ai.fallback import LLM_FALLBACK_MESSAGE
from race_engineer.ai.llm.client import OpenAiChatClient
from race_engineer.ai.llm.errors import LlmErrorCode
from race_engineer.ai.models import EngineerAskResult
from race_engineer.ai.prompt.builder import (
    DEFAULT_MAX_RESPONSE_WORDS,
    build_engineer_messages,
    enforce_word_limit,
)
from race_engineer.context.models import EngineerContext
from race_engineer.context.validation import validate_engineer_context


class EngineerAiService:
    """Build grounded prompts and request LLM completions."""

    def __init__(self, llm_client: OpenAiChatClient) -> None:
        self._llm_client = llm_client

    def ask(
        self,
        user_text: str,
        context: EngineerContext,
        *,
        intent: str | None = None,
        max_response_words: int = DEFAULT_MAX_RESPONSE_WORDS,
    ) -> EngineerAskResult:
        validate_engineer_context(context)
        messages = build_engineer_messages(
            user_text=user_text,
            context=context,
            intent=intent,
            max_response_words=max_response_words,
        )
        result = self._llm_client.complete(messages)
        if not result.success or result.data is None:
            return EngineerAskResult(
                text=LLM_FALLBACK_MESSAGE,
                fallback_used=True,
                error_code=result.error_code or LlmErrorCode.PROVIDER_ERROR,
            )

        limited_text = enforce_word_limit(result.data.text, max_response_words)
        return EngineerAskResult(
            text=limited_text,
            model=result.data.model,
            latency_ms=result.data.latency_ms,
            prompt_tokens=result.data.prompt_tokens,
            completion_tokens=result.data.completion_tokens,
        )
