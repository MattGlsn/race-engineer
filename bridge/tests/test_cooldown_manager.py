from race_engineer.proactive.cooldown import CooldownManager
from race_engineer.proactive.cooldown.models import CooldownConfig
from race_engineer.proactive.triggers.models import TriggerEvent, TriggerType


def _event(trigger_type: TriggerType, **payload: object) -> TriggerEvent:
    return TriggerEvent(type=trigger_type, payload=payload)


def test_filter_allows_first_event_when_idle() -> None:
    manager = CooldownManager(
        config=CooldownConfig(global_interval_seconds=10.0),
    )
    events = (_event(TriggerType.INCIDENT), _event(TriggerType.FUEL))

    allowed = manager.filter(events, now=100.0)

    assert allowed == (_event(TriggerType.INCIDENT),)


def test_filter_blocks_burst_within_global_window() -> None:
    manager = CooldownManager(
        config=CooldownConfig(global_interval_seconds=10.0),
    )
    manager.filter((_event(TriggerType.INCIDENT),), now=100.0)

    blocked = manager.filter((_event(TriggerType.FUEL),), now=105.0)

    assert blocked == ()


def test_filter_allows_event_after_global_window() -> None:
    manager = CooldownManager(
        config=CooldownConfig(global_interval_seconds=10.0),
    )
    manager.filter((_event(TriggerType.INCIDENT),), now=100.0)

    allowed = manager.filter((_event(TriggerType.FUEL),), now=110.0)

    assert allowed == (_event(TriggerType.FUEL),)


def test_filter_returns_empty_for_no_events() -> None:
    manager = CooldownManager()

    assert manager.filter(()) == ()


def test_reset_clears_global_throttle() -> None:
    manager = CooldownManager(
        config=CooldownConfig(global_interval_seconds=10.0),
    )
    manager.filter((_event(TriggerType.INCIDENT),), now=100.0)
    manager.reset()

    allowed = manager.filter((_event(TriggerType.FUEL),), now=105.0)

    assert allowed == (_event(TriggerType.FUEL),)


def test_begin_session_resets_throttle_state() -> None:
    manager = CooldownManager(
        config=CooldownConfig(global_interval_seconds=10.0),
    )
    manager.filter((_event(TriggerType.INCIDENT),), now=100.0)

    manager.begin_session("spa|race")

    allowed = manager.filter((_event(TriggerType.FUEL),), now=105.0)

    assert allowed == (_event(TriggerType.FUEL),)


def test_filter_blocks_repeat_trigger_before_type_cooldown() -> None:
    config = CooldownConfig(
        global_interval_seconds=0.0,
        trigger_intervals_seconds={TriggerType.FUEL: 60.0},
    )
    manager = CooldownManager(config=config)
    manager.filter((_event(TriggerType.FUEL),), now=100.0)

    blocked = manager.filter((_event(TriggerType.FUEL),), now=130.0)

    assert blocked == ()


def test_filter_allows_repeat_trigger_after_type_cooldown() -> None:
    config = CooldownConfig(
        global_interval_seconds=0.0,
        trigger_intervals_seconds={TriggerType.FUEL: 60.0},
    )
    manager = CooldownManager(config=config)
    manager.filter((_event(TriggerType.FUEL),), now=100.0)

    allowed = manager.filter((_event(TriggerType.FUEL),), now=160.0)

    assert allowed == (_event(TriggerType.FUEL),)


def test_filter_prefers_incident_over_fastest_lap_in_burst() -> None:
    manager = CooldownManager(
        config=CooldownConfig(global_interval_seconds=10.0),
    )
    events = (
        _event(TriggerType.FASTEST_LAP),
        _event(TriggerType.INCIDENT),
    )

    allowed = manager.filter(events, now=100.0)

    assert allowed == (_event(TriggerType.INCIDENT),)


def test_filter_allows_incident_during_global_throttle() -> None:
    manager = CooldownManager(
        config=CooldownConfig(global_interval_seconds=10.0),
    )
    manager.filter((_event(TriggerType.FASTEST_LAP),), now=100.0)

    allowed = manager.filter((_event(TriggerType.INCIDENT),), now=105.0)

    assert allowed == (_event(TriggerType.INCIDENT),)


def test_filter_allows_critical_fuel_during_global_throttle() -> None:
    manager = CooldownManager(
        config=CooldownConfig(global_interval_seconds=10.0),
    )
    manager.filter((_event(TriggerType.GAP_CLOSING_AHEAD),), now=100.0)

    allowed = manager.filter(
        (_event(TriggerType.FUEL, risk_level="critical"),),
        now=105.0,
    )

    assert allowed == (_event(TriggerType.FUEL, risk_level="critical"),)


def test_filter_prefers_critical_fuel_over_gap_in_burst() -> None:
    manager = CooldownManager(
        config=CooldownConfig(global_interval_seconds=10.0),
    )
    events = (
        _event(TriggerType.GAP_CLOSING_AHEAD),
        _event(TriggerType.FUEL, risk_level="critical"),
    )

    allowed = manager.filter(events, now=100.0)

    assert allowed == (_event(TriggerType.FUEL, risk_level="critical"),)
