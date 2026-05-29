from collections.abc import Mapping

from race_engineer.ai.prompt.models import DEFAULT_PERSONALITY_MODE, PersonalityMode

PERSONALITY_INSTRUCTIONS: Mapping[PersonalityMode, str] = {
    PersonalityMode.CALM: (
        "Tone: calm and steady, like a relaxed radio engineer. "
        "Use plain language, no hype, and keep emotions level."
    ),
    PersonalityMode.DIRECT: (
        "Tone: direct and factual. Lead with the answer, minimal filler, "
        "professional pit-wall brevity."
    ),
    PersonalityMode.INTENSE: (
        "Tone: urgent and energetic, like a race engineer under pressure. "
        "Stay concise, use decisive phrasing, but do not shout or exaggerate facts."
    ),
}


def personality_instructions(mode: PersonalityMode | None = None) -> str:
    """Return tone instructions for the selected personality mode."""
    selected = mode or DEFAULT_PERSONALITY_MODE
    return PERSONALITY_INSTRUCTIONS[selected]
