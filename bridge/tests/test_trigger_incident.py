from race_engineer.proactive.triggers.incident import evaluate_incident
from race_engineer.proactive.triggers.models import TriggerSnapshot, TriggerType


def test_incident_fires_on_count_increase() -> None:
    snapshot = TriggerSnapshot(incident_count=2)

    event, last_count = evaluate_incident(
        snapshot,
        last_incident_count=1,
    )

    assert event is not None
    assert event.type == TriggerType.INCIDENT
    assert event.payload["incident_count"] == 2
    assert event.payload["previous_incident_count"] == 1
    assert last_count == 2


def test_incident_does_not_repeat_for_same_count() -> None:
    snapshot = TriggerSnapshot(incident_count=2)

    event, last_count = evaluate_incident(
        snapshot,
        last_incident_count=2,
    )

    assert event is None
    assert last_count == 2


def test_incident_seeds_baseline_without_firing() -> None:
    snapshot = TriggerSnapshot(incident_count=1)

    event, last_count = evaluate_incident(
        snapshot,
        last_incident_count=None,
    )

    assert event is None
    assert last_count == 1
