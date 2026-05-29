from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SynthesisResult:
    """Metadata for a completed engineer voice synthesis."""

    text: str
    duration_ms: int | None = None
