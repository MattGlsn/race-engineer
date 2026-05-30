from race_engineer.proactive.triggers.gap import evaluate_gap
from race_engineer.proactive.triggers.models import TriggerSnapshot, TriggerType


def test_gap_ahead_fires_when_crossing_threshold() -> None:
    snapshot = TriggerSnapshot(gap_ahead_seconds=0.8)

    events, ahead_armed, behind_armed = evaluate_gap(
        snapshot,
        gap_ahead_armed=True,
        gap_behind_armed=True,
    )

    assert len(events) == 1
    assert events[0].type == TriggerType.GAP_CLOSING_AHEAD
    assert events[0].payload["gap_seconds"] == 0.8
    assert ahead_armed is False
    assert behind_armed is True


def test_gap_ahead_does_not_repeat_until_rearmed() -> None:
    snapshot = TriggerSnapshot(gap_ahead_seconds=0.6)

    events, ahead_armed, _ = evaluate_gap(
        snapshot,
        gap_ahead_armed=False,
        gap_behind_armed=True,
    )

    assert events == ()
    assert ahead_armed is False


def test_gap_ahead_rearms_when_gap_opens() -> None:
    snapshot = TriggerSnapshot(gap_ahead_seconds=1.5)

    events, ahead_armed, _ = evaluate_gap(
        snapshot,
        gap_ahead_armed=False,
        gap_behind_armed=True,
    )

    assert events == ()
    assert ahead_armed is True


def test_gap_behind_fires_when_crossing_threshold() -> None:
    snapshot = TriggerSnapshot(gap_behind_seconds=0.7)

    events, ahead_armed, behind_armed = evaluate_gap(
        snapshot,
        gap_ahead_armed=True,
        gap_behind_armed=True,
    )

    assert len(events) == 1
    assert events[0].type == TriggerType.GAP_CLOSING_BEHIND
    assert ahead_armed is True
    assert behind_armed is False
