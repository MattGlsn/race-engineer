import re

DEFAULT_MAX_RESPONSE_WORDS = 30

RADIO_STYLE_RULES = """\
## Radio style

- You are the race engineer on pit-wall radio speaking directly to your pilot.
- Lead with the answer. Use direct address ("Copy", "You're P3") — not third-person essays.
- No markdown, bullet lists, numbered lists, or filler ("Based on the context…").
- Prefer one short sentence. Use a second only if a critical extra fact is needed.
- Keep it brief enough to say clearly over engine noise.
"""

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_BULLET_RE = re.compile(r"^\s*[-*]\s+", re.MULTILINE)
_NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+", re.MULTILINE)
_WHITESPACE_RE = re.compile(r"\s+")


def _strip_markdown(text: str) -> str:
    text = _BOLD_RE.sub(r"\1", text)
    text = _BULLET_RE.sub("", text)
    text = _NUMBERED_RE.sub("", text)
    return text


def wrap_engineer_reply(text: str, *, max_words: int = DEFAULT_MAX_RESPONSE_WORDS) -> str:
    """Clean and shorten an LLM reply for pit-wall radio delivery."""
    from race_engineer.ai.prompt.builder import enforce_word_limit

    cleaned = _strip_markdown(text.strip())
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()
    return enforce_word_limit(cleaned, max_words)
