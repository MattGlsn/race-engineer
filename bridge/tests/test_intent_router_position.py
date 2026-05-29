import pytest

from race_engineer.voice.intent.models import VoiceIntent
from race_engineer.voice.intent.router import route_intent


@pytest.mark.parametrize(
    "utterance",
    [
        "what position am I in",
        "where am I running",
        "what is my class position",
        "overall standing",
        "what place are we",
        "am I still in the standings",
    ],
)
def test_position_intent(utterance: str) -> None:
    assert route_intent(utterance).intent == VoiceIntent.POSITION
