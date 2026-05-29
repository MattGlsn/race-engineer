from race_engineer.ai.fallback import LLM_FALLBACK_MESSAGE
from race_engineer.ai.llm.client import OpenAiChatClient
from race_engineer.ai.llm.errors import LlmErrorCode
from race_engineer.ai.llm.metadata import CompletionMetadata, log_completion_metadata
from race_engineer.ai.models import EngineerAskResult
from race_engineer.ai.prompt.builder import (
    DEFAULT_MAX_RESPONSE_WORDS,
    build_engineer_messages,
    enforce_word_limit,
)
from race_engineer.context.models import EngineerContext
from race_engineer.context.validation import serialize_context, validate_engineer_context


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
        context_bytes = len(serialize_context(context).encode("utf-8"))
        messages = build_engineer_messages(
            user_text=user_text,
            context=context,
            intent=intent,
            max_response_words=max_response_words,
        )
        result = self._llm_client.complete(messages)
        if not result.success or result.data is None:
            ask_result = EngineerAskResult(
                text=LLM_FALLBACK_MESSAGE,
                fallback_used=True,
                error_code=result.error_code or LlmErrorCode.PROVIDER_ERROR,
            )
            log_completion_metadata(
                CompletionMetadata(
                    context_bytes=context_bytes,
                    response_word_count=len(ask_result.text.split()),
                    fallback_used=True,
                    error_code=ask_result.error_code,
                )
            )
            return ask_result

        limited_text = enforce_word_limit(result.data.text, max_response_words)
        ask_result = EngineerAskResult(
            text=limited_text,
            model=result.data.model,
            latency_ms=result.data.latency_ms,
            prompt_tokens=result.data.prompt_tokens,
            completion_tokens=result.data.completion_tokens,
        )
        log_completion_metadata(
            CompletionMetadata(
                context_bytes=context_bytes,
                response_word_count=len(ask_result.text.split()),
                model=ask_result.model,
                latency_ms=ask_result.latency_ms,
                prompt_tokens=ask_result.prompt_tokens,
                completion_tokens=ask_result.completion_tokens,
                fallback_used=False,
            )
        )
        return ask_result
