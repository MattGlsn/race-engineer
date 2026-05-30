from race_engineer.proactive.triggers.fastest_lap import evaluate_fastest_lap
from race_engineer.proactive.triggers.models import TriggerSnapshot, TriggerType


def test_fastest_lap_fires_on_improvement() -> None:
    snapshot = TriggerSnapshot(player_best_lap_time=89.5)

    event, last_best = evaluate_fastest_lap(
        snapshot,
        last_best_lap_time=90.0,
    )

    assert event is not None
    assert event.type == TriggerType.FASTEST_LAP
    assert event.payload["best_lap_time"] == 89.5
    assert event.payload["previous_best_lap_time"] == 90.0
    assert last_best == 89.5


def test_fastest_lap_does_not_repeat_for_same_best() -> None:
    snapshot = TriggerSnapshot(player_best_lap_time=89.5)

    event, last_best = evaluate_fastest_lap(
        snapshot,
        last_best_lap_time=89.5,
    )

    assert event is None
    assert last_best == 89.5


def test_fastest_lap_seeds_baseline_without_firing() -> None:
    snapshot = TriggerSnapshot(player_best_lap_time=90.0)

    event, last_best = evaluate_fastest_lap(
        snapshot,
        last_best_lap_time=None,
    )

    assert event is None
    assert last_best == 90.0
