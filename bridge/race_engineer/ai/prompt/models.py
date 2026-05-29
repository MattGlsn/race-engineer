from enum import StrEnum


class PersonalityMode(StrEnum):
    """Radio engineer tone variants."""

    CALM = "calm"
    DIRECT = "direct"
    INTENSE = "intense"


DEFAULT_PERSONALITY_MODE = PersonalityMode.DIRECT
