from race_engineer.voice.intent.models import IntentResult, VoiceIntent
from race_engineer.voice.intent.normalize import contains_phrase, normalize_transcript
from race_engineer.voice.intent.rules import INTENT_RULES


class IntentRouter:
    """Classify driver speech into telemetry query intents."""

    def route(self, text: str) -> IntentResult:
        stripped = text.strip()
        if not stripped:
            return IntentResult(intent=VoiceIntent.UNKNOWN, text="")

        normalized = normalize_transcript(stripped)
        if not normalized:
            return IntentResult(intent=VoiceIntent.UNKNOWN, text=stripped)

        for intent, phrases in INTENT_RULES:
            for phrase in phrases:
                if contains_phrase(normalized, phrase):
                    return IntentResult(intent=intent, text=stripped)

        return IntentResult(intent=VoiceIntent.UNKNOWN, text=stripped)


def route_intent(text: str) -> IntentResult:
    """Route a transcript string to a voice intent."""
    return IntentRouter().route(text)
