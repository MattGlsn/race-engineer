from race_engineer.fuel.projection.models import FuelRiskLevel
from race_engineer.proactive.triggers import TriggerEngine, TriggerSnapshot, TriggerType


def _snapshot(**overrides: object) -> TriggerSnapshot:
    defaults = {
        "session_key": "spa|race",
        "player_best_lap_time": 90.0,
        "incident_count": 0,
        "fuel_risk_level": FuelRiskLevel.SAFE,
        "gap_ahead_seconds": 2.0,
        "gap_behind_seconds": 2.0,
    }
    defaults.update(overrides)
    return TriggerSnapshot(**defaults)  # type: ignore[arg-type]


def test_engine_resets_on_session_change() -> None:
    engine = TriggerEngine()
    engine.evaluate(_snapshot(session_key="spa|race", player_best_lap_time=90.0))

    events = engine.evaluate(
        _snapshot(
            session_key="monza|race",
            player_best_lap_time=89.0,
            incident_count=1,
        ),
    )

    assert events == ()


def test_engine_emits_multiple_triggers_in_one_tick() -> None:
    engine = TriggerEngine()
    engine.evaluate(_snapshot(player_best_lap_time=90.0, incident_count=0))

    events = engine.evaluate(
        _snapshot(
            player_best_lap_time=89.5,
            incident_count=1,
            fuel_risk_level=FuelRiskLevel.CAUTION,
            gap_ahead_seconds=0.8,
        ),
    )

    types = {event.type for event in events}
    assert TriggerType.FASTEST_LAP in types
    assert TriggerType.INCIDENT in types
    assert TriggerType.FUEL in types
    assert TriggerType.GAP_CLOSING_AHEAD in types


def test_engine_deduplicates_repeated_snapshots() -> None:
    engine = TriggerEngine()
    engine.evaluate(_snapshot(player_best_lap_time=90.0))

    first = engine.evaluate(_snapshot(player_best_lap_time=89.5))
    second = engine.evaluate(_snapshot(player_best_lap_time=89.5))

    assert len(first) == 1
    assert second == ()
