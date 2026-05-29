from dataclasses import dataclass
from typing import Generic, TypeVar

from race_engineer.voice.stt.errors import VoiceErrorCode

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class VoicePipelineResult(Generic[T]):
    """Success or typed failure for voice pipeline operations."""

    success: bool
    data: T | None = None
    error_code: VoiceErrorCode | None = None
    message: str | None = None

    @classmethod
    def ok(cls, data: T) -> "VoicePipelineResult[T]":
        return cls(success=True, data=data)

    @classmethod
    def fail(
        cls,
        *,
        error_code: VoiceErrorCode,
        message: str,
    ) -> "VoicePipelineResult[T]":
        return cls(success=False, error_code=error_code, message=message)
