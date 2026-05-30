from race_engineer.proactive.triggers.models import TriggerEvent, TriggerSnapshot, TriggerType


def evaluate_incident(
    snapshot: TriggerSnapshot,
    *,
    last_incident_count: int | None,
) -> tuple[TriggerEvent | None, int | None]:
    """Return an incident trigger when the player's incident count increases."""
    count = snapshot.incident_count
    if count is None:
        return None, last_incident_count

    if last_incident_count is None:
        return None, count

    if count <= last_incident_count:
        return None, count

    return (
        TriggerEvent(
            type=TriggerType.INCIDENT,
            payload={
                "incident_count": count,
                "previous_incident_count": last_incident_count,
            },
        ),
        count,
    )
