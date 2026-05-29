from collections.abc import Sequence

from race_engineer.voice.intent.models import VoiceIntent

CorpusEntry = tuple[str, VoiceIntent]

# Curated driver utterances for accuracy benchmarking.
INTENT_CORPUS: tuple[CorpusEntry, ...] = (
    ("give me some coaching", VoiceIntent.COACHING),
    ("coach me through turn one", VoiceIntent.COACHING),
    ("what is the racing line here", VoiceIntent.COACHING),
    ("any tips on trail braking", VoiceIntent.COACHING),
    ("how can I brake later", VoiceIntent.COACHING),
    ("help me go faster", VoiceIntent.COACHING),
    ("advice for the apex", VoiceIntent.COACHING),
    ("improve my technique in turn three", VoiceIntent.COACHING),
    ("should I brake earlier", VoiceIntent.COACHING),
    ("need a faster lap", VoiceIntent.COACHING),
    ("how much fuel do I have left", VoiceIntent.FUEL),
    ("what is my fuel level", VoiceIntent.FUEL),
    ("fuel remaining", VoiceIntent.FUEL),
    ("do I have enough fuel to finish", VoiceIntent.FUEL),
    ("what is our fuel consumption", VoiceIntent.FUEL),
    ("how many liters in the tank", VoiceIntent.FUEL),
    ("will I make it on fuel", VoiceIntent.FUEL),
    ("need to save fuel", VoiceIntent.FUEL),
    ("gas left in the tank", VoiceIntent.FUEL),
    ("check the fuel", VoiceIntent.FUEL),
    ("what position am I in", VoiceIntent.POSITION),
    ("where am I running", VoiceIntent.POSITION),
    ("what is my class position", VoiceIntent.POSITION),
    ("overall standing", VoiceIntent.POSITION),
    ("what place are we", VoiceIntent.POSITION),
    ("am I still in the standings", VoiceIntent.POSITION),
    ("my position in class", VoiceIntent.POSITION),
    ("overall position", VoiceIntent.POSITION),
    ("where am I on track", VoiceIntent.POSITION),
    ("what is my place", VoiceIntent.POSITION),
    ("what is my gap ahead", VoiceIntent.GAP),
    ("gap to the car behind", VoiceIntent.GAP),
    ("interval to the leader", VoiceIntent.GAP),
    ("how far behind is the car behind", VoiceIntent.GAP),
    ("what is the delta ahead", VoiceIntent.GAP),
    ("gap behind", VoiceIntent.GAP),
    ("car ahead gap", VoiceIntent.GAP),
    ("seconds behind", VoiceIntent.GAP),
    ("time gap to p1", VoiceIntent.GAP),
    ("what is the interval ahead", VoiceIntent.GAP),
    ("what was my last lap time", VoiceIntent.LAP),
    ("best lap time", VoiceIntent.LAP),
    ("how was sector two", VoiceIntent.LAP),
    ("sector times", VoiceIntent.LAP),
    ("what was that lap", VoiceIntent.LAP),
    ("personal best lap", VoiceIntent.LAP),
    ("current lap time", VoiceIntent.LAP),
    ("lap times", VoiceIntent.LAP),
    ("previous lap", VoiceIntent.LAP),
    ("sector 3 time", VoiceIntent.LAP),
    ("hello there", VoiceIntent.UNKNOWN),
    ("radio check", VoiceIntent.UNKNOWN),
    ("pit this lap", VoiceIntent.UNKNOWN),
    ("copy that", VoiceIntent.UNKNOWN),
    ("thanks engineer", VoiceIntent.UNKNOWN),
)


def corpus_entries() -> Sequence[CorpusEntry]:
    return INTENT_CORPUS
