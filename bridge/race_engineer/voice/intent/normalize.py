import re

_NON_WORD_RE = re.compile(r"[^\w\s']")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_transcript(text: str) -> str:
    """Lowercase and strip punctuation for phrase matching."""
    lowered = text.lower().strip()
    cleaned = _NON_WORD_RE.sub(" ", lowered)
    return _WHITESPACE_RE.sub(" ", cleaned).strip()


def contains_phrase(normalized: str, phrase: str) -> bool:
    """Return True when phrase appears in normalized text with word boundaries."""
    phrase = phrase.strip().lower()
    if not phrase:
        return False
    if " " in phrase:
        return phrase in normalized
    return re.search(rf"\b{re.escape(phrase)}\b", normalized) is not None
