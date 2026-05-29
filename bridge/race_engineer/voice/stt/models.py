from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TranscriptResult:
    """Structured transcript returned by the STT provider."""

    text: str
    language_code: str | None = None
    duration_ms: int | None = None
