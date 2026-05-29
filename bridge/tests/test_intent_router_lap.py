import pytest

from race_engineer.voice.intent.models import VoiceIntent
from race_engineer.voice.intent.router import route_intent


@pytest.mark.parametrize(
    "utterance",
    [
        "what was my last lap time",
        "best lap time",
        "how was sector two",
        "sector times",
        "what was that lap",
        "personal best lap",
    ],
)
def test_lap_intent(utterance: str) -> None:
    assert route_intent(utterance).intent == VoiceIntent.LAP
