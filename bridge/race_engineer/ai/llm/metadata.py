from __future__ import annotations

import logging
from dataclasses import dataclass

from race_engineer.ai.llm.errors import LlmErrorCode

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CompletionMetadata:
    """Non-sensitive metadata for an engineer LLM completion."""

    context_bytes: int
    response_word_count: int
    model: str | None = None
    latency_ms: int = 0
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    fallback_used: bool = False
    error_code: LlmErrorCode | None = None


def log_completion_metadata(metadata: CompletionMetadata) -> None:
    """Log LLM completion metadata without prompt or response body content."""
    logger.info(
        "engineer llm completion model=%s latency_ms=%s context_bytes=%s "
        "response_word_count=%s prompt_tokens=%s completion_tokens=%s "
        "fallback_used=%s error_code=%s",
        metadata.model,
        metadata.latency_ms,
        metadata.context_bytes,
        metadata.response_word_count,
        metadata.prompt_tokens,
        metadata.completion_tokens,
        metadata.fallback_used,
        metadata.error_code.value if metadata.error_code else None,
    )
