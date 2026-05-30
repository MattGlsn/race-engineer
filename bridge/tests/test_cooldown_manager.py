from race_engineer.proactive.cooldown import CooldownManager
from race_engineer.proactive.triggers.models import TriggerEvent, TriggerType


def _event(trigger_type: TriggerType) -> TriggerEvent:
    return TriggerEvent(type=trigger_type)


def test_filter_allows_first_event_when_idle() -> None:
    manager = CooldownManager(global_interval_seconds=10.0)
    events = (_event(TriggerType.INCIDENT), _event(TriggerType.FUEL))

    allowed = manager.filter(events, now=100.0)

    assert allowed == (_event(TriggerType.INCIDENT),)


def test_filter_blocks_burst_within_global_window() -> None:
    manager = CooldownManager(global_interval_seconds=10.0)
    manager.filter((_event(TriggerType.INCIDENT),), now=100.0)

    blocked = manager.filter((_event(TriggerType.FUEL),), now=105.0)

    assert blocked == ()


def test_filter_allows_event_after_global_window() -> None:
    manager = CooldownManager(global_interval_seconds=10.0)
    manager.filter((_event(TriggerType.INCIDENT),), now=100.0)

    allowed = manager.filter((_event(TriggerType.FUEL),), now=110.0)

    assert allowed == (_event(TriggerType.FUEL),)


def test_filter_returns_empty_for_no_events() -> None:
    manager = CooldownManager()

    assert manager.filter(()) == ()


def test_reset_clears_global_throttle() -> None:
    manager = CooldownManager(global_interval_seconds=10.0)
    manager.filter((_event(TriggerType.INCIDENT),), now=100.0)
    manager.reset()

    allowed = manager.filter((_event(TriggerType.FUEL),), now=105.0)

    assert allowed == (_event(TriggerType.FUEL),)


def test_begin_session_resets_throttle_state() -> None:
    manager = CooldownManager(global_interval_seconds=10.0)
    manager.filter((_event(TriggerType.INCIDENT),), now=100.0)

    manager.begin_session("spa|race")

    allowed = manager.filter((_event(TriggerType.FUEL),), now=105.0)

    assert allowed == (_event(TriggerType.FUEL),)
