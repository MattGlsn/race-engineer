from race_engineer.ai.prompt.builder import (
    DEFAULT_MAX_RESPONSE_WORDS,
    build_engineer_messages,
    build_system_prompt,
    enforce_word_limit,
)
from race_engineer.ai.prompt.safety import SAFETY_RULES
from race_engineer.context.aggregator import empty_engineer_context
from race_engineer.context.models import EngineerContext, RaceContextState, SessionContextState
from race_engineer.context.validation import validate_engineer_context


def test_build_system_prompt_includes_safety_and_word_limit() -> None:
    prompt = build_system_prompt()
    assert "race engineer" in prompt.lower()
    assert SAFETY_RULES.strip() in prompt
    assert str(DEFAULT_MAX_RESPONSE_WORDS) in prompt


def test_build_engineer_messages_embeds_context_and_question() -> None:
    context = EngineerContext(
        session=SessionContextState(track_name="Spa", session_type="Race", field_size=20),
        race=RaceContextState(overall_position=3, fuel_level=42.5),
        driver=empty_engineer_context().driver,
        analytics=empty_engineer_context().analytics,
    )
    validate_engineer_context(context)

    messages = build_engineer_messages(
        user_text="What's my fuel?",
        context=context,
        intent="fuel",
    )

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    user_content = messages[1]["content"]
    assert "Spa" in user_content
    assert "What's my fuel?" in user_content
    assert "fuel" in user_content


def test_build_engineer_messages_with_disconnected_context() -> None:
    context = empty_engineer_context()
    messages = build_engineer_messages(user_text="Where am I?", context=context)
    assert '"session"' in messages[1]["content"]
    assert "Where am I?" in messages[1]["content"]


def test_enforce_word_limit_truncates_long_replies() -> None:
    text = " ".join(f"word{i}" for i in range(60))
    assert len(enforce_word_limit(text).split()) == DEFAULT_MAX_RESPONSE_WORDS
