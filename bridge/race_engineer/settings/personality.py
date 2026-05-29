from race_engineer.ai.prompt.models import DEFAULT_PERSONALITY_MODE, PersonalityMode


class PersonalitySettings:
    """In-memory engineer tone preference shared by API and voice pipeline."""

    def __init__(self, mode: PersonalityMode | None = None) -> None:
        self._mode = mode or DEFAULT_PERSONALITY_MODE

    @property
    def mode(self) -> PersonalityMode:
        return self._mode

    def set_mode(self, mode: PersonalityMode) -> None:
        self._mode = mode
