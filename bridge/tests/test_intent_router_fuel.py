import pytest

from race_engineer.voice.intent.models import VoiceIntent
from race_engineer.voice.intent.router import route_intent


@pytest.mark.parametrize(
    "utterance",
    [
        "how much fuel do I have left",
        "what is my fuel level",
        "fuel remaining",
        "do I have enough fuel to finish",
        "what is our fuel consumption",
        "how many liters in the tank",
        "will I make it on fuel",
        "need to save fuel",
    ],
)
def test_fuel_intent(utterance: str) -> None:
    assert route_intent(utterance).intent == VoiceIntent.FUEL
