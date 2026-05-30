from race_engineer.ai.prompt.builder import build_system_prompt
from race_engineer.ai.prompt.wrapper import (
    DEFAULT_MAX_RESPONSE_WORDS,
    RADIO_STYLE_RULES,
    wrap_engineer_reply,
)


def test_default_max_response_words_is_30() -> None:
    assert DEFAULT_MAX_RESPONSE_WORDS == 30


def test_build_system_prompt_includes_radio_style_rules() -> None:
    prompt = build_system_prompt()
    assert "Radio style" in prompt
    assert "speaking directly to your pilot" in prompt


def test_wrap_engineer_reply_strips_markdown() -> None:
    result = wrap_engineer_reply("**Copy.** You're in P3.")
    assert result == "Copy. You're in P3."


def test_wrap_engineer_reply_strips_bullet_lists() -> None:
    result = wrap_engineer_reply("- P3\n- Gap plus two")
    assert result == "P3 Gap plus two"


def test_wrap_engineer_reply_truncates_at_max_words() -> None:
    long_text = " ".join(f"word{i}" for i in range(40))
    result = wrap_engineer_reply(long_text)
    assert len(result.split()) == 30


def test_wrap_engineer_reply_leaves_short_reply_unchanged() -> None:
    text = "Copy. P3, gap plus two."
    assert wrap_engineer_reply(text) == text


def test_wrap_engineer_reply_handles_empty_string() -> None:
    assert wrap_engineer_reply("") == ""
    assert wrap_engineer_reply("   ") == ""


def test_radio_style_rules_mentions_pilot() -> None:
    assert "pilot" in RADIO_STYLE_RULES
