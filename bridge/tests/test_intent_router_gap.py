import pytest

from race_engineer.voice.intent.models import VoiceIntent
from race_engineer.voice.intent.router import route_intent


@pytest.mark.parametrize(
    "utterance",
    [
        "what is my gap ahead",
        "gap to the car behind",
        "interval to the leader",
        "how far behind is the car behind",
        "what is the delta ahead",
        "gap behind",
    ],
)
def test_gap_intent(utterance: str) -> None:
    assert route_intent(utterance).intent == VoiceIntent.GAP
