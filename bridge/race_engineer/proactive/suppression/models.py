from dataclasses import dataclass

DEFAULT_MAX_PENDING_TRIGGERS = 8
DEFAULT_MAX_PENDING_AGE_SECONDS = 30.0
DEFAULT_MAX_PENDING_SPEECH = 4


@dataclass(frozen=True, slots=True)
class SuppressionConfig:
    max_pending_triggers: int = DEFAULT_MAX_PENDING_TRIGGERS
    max_pending_age_seconds: float = DEFAULT_MAX_PENDING_AGE_SECONDS
    max_pending_speech: int = DEFAULT_MAX_PENDING_SPEECH
