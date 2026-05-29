from dataclasses import dataclass

from race_engineer.ai.llm.errors import LlmErrorCode


@dataclass(frozen=True, slots=True)
class EngineerAskResult:
    """Structured engineer reply returned to callers."""

    text: str
    model: str | None = None
    latency_ms: int = 0
    fallback_used: bool = False
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    error_code: LlmErrorCode | None = None

    @property
    def success(self) -> bool:
        return self.error_code is None or self.fallback_used
