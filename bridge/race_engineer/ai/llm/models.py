from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CompletionResult:
    """Structured text completion returned by the LLM provider."""

    text: str
    model: str
    latency_ms: int
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
