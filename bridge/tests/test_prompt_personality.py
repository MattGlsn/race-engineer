import pytest

from race_engineer.ai.prompt.models import DEFAULT_PERSONALITY_MODE, PersonalityMode
from race_engineer.ai.prompt.personality import (
    PERSONALITY_INSTRUCTIONS,
    personality_instructions,
)


def test_default_personality_mode_is_direct() -> None:
    assert DEFAULT_PERSONALITY_MODE == PersonalityMode.DIRECT
    assert personality_instructions() == PERSONALITY_INSTRUCTIONS[PersonalityMode.DIRECT]


@pytest.mark.parametrize("mode", list(PersonalityMode))
def test_each_personality_mode_has_distinct_instructions(mode: PersonalityMode) -> None:
    instructions = personality_instructions(mode)
    assert instructions
    assert instructions == PERSONALITY_INSTRUCTIONS[mode]


def test_personality_modes_are_unique() -> None:
    values = list(PERSONALITY_INSTRUCTIONS.values())
    assert len(values) == len(set(values))
