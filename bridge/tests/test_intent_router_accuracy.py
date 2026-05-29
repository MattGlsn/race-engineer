from race_engineer.voice.intent.corpus import INTENT_CORPUS
from race_engineer.voice.intent.router import route_intent

MIN_ACCURACY = 0.95


def test_intent_corpus_accuracy() -> None:
    correct = 0
    failures: list[str] = []

    for utterance, expected in INTENT_CORPUS:
        actual = route_intent(utterance).intent
        if actual == expected:
            correct += 1
        else:
            failures.append(f"{utterance!r}: expected {expected.value}, got {actual.value}")

    accuracy = correct / len(INTENT_CORPUS)
    assert accuracy >= MIN_ACCURACY, (
        f"accuracy {accuracy:.1%} below {MIN_ACCURACY:.0%}; failures: {failures}"
    )
