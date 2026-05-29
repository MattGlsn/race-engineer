from typing import TypedDict

from race_engineer.ai.prompt.models import DEFAULT_PERSONALITY_MODE, PersonalityMode
from race_engineer.ai.prompt.personality import personality_instructions
from race_engineer.ai.prompt.safety import SAFETY_RULES
from race_engineer.context.models import EngineerContext
from race_engineer.context.validation import serialize_context

DEFAULT_MAX_RESPONSE_WORDS = 50

ENGINEER_ROLE = """\
You are the driver's AI race engineer for iRacing. You speak over the radio in short, clear replies.
Answer the driver's question using only the race context JSON provided with their message.
"""


class ChatMessage(TypedDict):
    role: str
    content: str


def build_system_prompt(
    personality: PersonalityMode | None = None,
    *,
    max_response_words: int = DEFAULT_MAX_RESPONSE_WORDS,
) -> str:
    """Compose the full system prompt for the AI race engineer."""
    mode = personality or DEFAULT_PERSONALITY_MODE
    sections = (
        ENGINEER_ROLE.strip(),
        personality_instructions(mode),
        SAFETY_RULES.strip(),
        (
            f"## Response length\n\n"
            f"Default to at most {max_response_words} words. "
            "Only exceed that if the driver explicitly asks for more detail."
        ),
    )
    return "\n\n".join(sections)


def build_user_message(
    *,
    user_text: str,
    context: EngineerContext,
    intent: str | None = None,
) -> str:
    """Build the user turn with embedded race context and driver question."""
    context_json = serialize_context(context)
    intent_line = f"Detected intent: {intent}\n" if intent else ""
    question = user_text.strip() or "(no question provided)"
    return (
        f"{intent_line}"
        "Race context JSON:\n"
        f"{context_json}\n\n"
        f"Driver message: {question}"
    )


def build_engineer_messages(
    *,
    user_text: str,
    context: EngineerContext,
    intent: str | None = None,
    personality: PersonalityMode | None = None,
    max_response_words: int = DEFAULT_MAX_RESPONSE_WORDS,
) -> list[ChatMessage]:
    """Build chat messages for an LLM completion request."""
    return [
        {
            "role": "system",
            "content": build_system_prompt(
                personality,
                max_response_words=max_response_words,
            ),
        },
        {
            "role": "user",
            "content": build_user_message(
                user_text=user_text,
                context=context,
                intent=intent,
            ),
        },
    ]


def enforce_word_limit(text: str, max_words: int = DEFAULT_MAX_RESPONSE_WORDS) -> str:
    """Truncate reply text to a maximum word count."""
    stripped = text.strip()
    if not stripped:
        return stripped

    words = stripped.split()
    if len(words) <= max_words:
        return stripped

    return " ".join(words[:max_words])
