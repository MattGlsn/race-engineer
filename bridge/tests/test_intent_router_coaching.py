import pytest

from race_engineer.voice.intent.models import VoiceIntent
from race_engineer.voice.intent.router import route_intent


@pytest.mark.parametrize(
    "utterance",
    [
        "give me some coaching",
        "coach me through turn one",
        "what is the racing line here",
        "any tips on trail braking",
        "how can I brake later",
        "help me go faster",
        "advice for the apex",
    ],
)
def test_coaching_intent(utterance: str) -> None:
    assert route_intent(utterance).intent == VoiceIntent.COACHING


@pytest.mark.parametrize(
    "utterance",
    [
        "",
        "   ",
        "hello there",
        "radio check",
        "pit this lap",
    ],
)
def test_unknown_intent(utterance: str) -> None:
    assert route_intent(utterance).intent == VoiceIntent.UNKNOWN
