from race_engineer.proactive.triggers.models import TriggerEvent, TriggerSnapshot, TriggerType


def evaluate_fastest_lap(
    snapshot: TriggerSnapshot,
    *,
    last_best_lap_time: float | None,
) -> tuple[TriggerEvent | None, float | None]:
    """Return a fastest-lap trigger when the player's best lap improves."""
    best_lap = snapshot.player_best_lap_time
    if best_lap is None:
        return None, last_best_lap_time

    if last_best_lap_time is not None and best_lap >= last_best_lap_time:
        return None, best_lap

    if last_best_lap_time is None:
        return None, best_lap

    return (
        TriggerEvent(
            type=TriggerType.FASTEST_LAP,
            payload={
                "best_lap_time": best_lap,
                "previous_best_lap_time": last_best_lap_time,
            },
        ),
        best_lap,
    )
