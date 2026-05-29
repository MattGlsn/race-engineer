from race_engineer.ai.llm.client import OpenAiChatClient
from race_engineer.ai.llm.models import CompletionResult
from race_engineer.ai.llm.result import LlmResult
from race_engineer.ai.prompt.builder import build_engineer_messages
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
    ) -> LlmResult[CompletionResult]:
        validate_engineer_context(context)
        messages = build_engineer_messages(
            user_text=user_text,
            context=context,
            intent=intent,
        )
        return self._llm_client.complete(messages)
