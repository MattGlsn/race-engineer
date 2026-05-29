from dataclasses import dataclass
from typing import Generic, TypeVar

from race_engineer.ai.llm.errors import LlmErrorCode

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class LlmResult(Generic[T]):
    """Success or typed failure for LLM operations."""

    success: bool
    data: T | None = None
    error_code: LlmErrorCode | None = None
    message: str | None = None

    @classmethod
    def ok(cls, data: T) -> "LlmResult[T]":
        return cls(success=True, data=data)

    @classmethod
    def fail(
        cls,
        *,
        error_code: LlmErrorCode,
        message: str,
    ) -> "LlmResult[T]":
        return cls(success=False, error_code=error_code, message=message)
