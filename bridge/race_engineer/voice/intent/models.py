from dataclasses import dataclass
from enum import StrEnum


class VoiceIntent(StrEnum):
    COACHING = "coaching"
    FUEL = "fuel"
    POSITION = "position"
    GAP = "gap"
    LAP = "lap"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class IntentResult:
    intent: VoiceIntent
    text: str
