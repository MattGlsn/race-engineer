from race_engineer.proactive.triggers.models import TriggerEvent, TriggerSnapshot, TriggerType

GAP_CLOSE_THRESHOLD_SECONDS = 1.0


def evaluate_gap(
    snapshot: TriggerSnapshot,
    *,
    gap_ahead_armed: bool,
    gap_behind_armed: bool,
) -> tuple[tuple[TriggerEvent, ...], bool, bool]:
    """Return gap triggers when intervals cross the close threshold."""
    events: list[TriggerEvent] = []

    gap_ahead = snapshot.gap_ahead_seconds
    if gap_ahead is not None:
        if gap_ahead >= GAP_CLOSE_THRESHOLD_SECONDS:
            gap_ahead_armed = True
        elif gap_ahead_armed:
            events.append(
                TriggerEvent(
                    type=TriggerType.GAP_CLOSING_AHEAD,
                    payload={"gap_seconds": gap_ahead},
                ),
            )
            gap_ahead_armed = False

    gap_behind = snapshot.gap_behind_seconds
    if gap_behind is not None:
        if gap_behind >= GAP_CLOSE_THRESHOLD_SECONDS:
            gap_behind_armed = True
        elif gap_behind_armed:
            events.append(
                TriggerEvent(
                    type=TriggerType.GAP_CLOSING_BEHIND,
                    payload={"gap_seconds": gap_behind},
                ),
            )
            gap_behind_armed = False

    return tuple(events), gap_ahead_armed, gap_behind_armed
