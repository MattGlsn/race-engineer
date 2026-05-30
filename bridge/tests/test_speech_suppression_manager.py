from race_engineer.fuel.projection.models import FuelRiskLevel
from race_engineer.proactive.suppression import (
    SpeechSuppressionManager,
    WorkloadMonitor,
)
from race_engineer.proactive.suppression.braking import BrakingConfig
from race_engineer.proactive.suppression.workload import WorkloadConfig
from race_engineer.proactive.triggers.models import TriggerEvent, TriggerType
from race_engineer.telemetry.models import TelemetrySnapshot


def _event(trigger_type: TriggerType, **payload: object) -> TriggerEvent:
    return TriggerEvent(type=trigger_type, payload=payload)


def _idle(monitor: WorkloadMonitor, *, now: float = 2.0) -> None:
    monitor.observe(
        TelemetrySnapshot(brake=0.0, steering=0.0, speed=30.0),
        now=now,
    )


def _busy(monitor: WorkloadMonitor, *, now: float = 1.0) -> None:
    monitor.observe(
        TelemetrySnapshot(brake=0.4, steering=0.0, speed=30.0),
        now=now,
    )


def test_defers_non_urgent_trigger_while_suppressed() -> None:
    workload = WorkloadMonitor()
    manager = SpeechSuppressionManager(workload)
    _busy(workload)

    released = manager.accept_trigger(_event(TriggerType.FUEL), now=1.0)

    assert released == ()
    assert manager.drain_triggers(now=1.0) == ()


def test_urgent_incident_bypasses_suppression() -> None:
    workload = WorkloadMonitor()
    manager = SpeechSuppressionManager(workload)
    _busy(workload)
    incident = _event(TriggerType.INCIDENT)

    released = manager.accept_trigger(incident, now=1.0)

    assert released == (incident,)


def test_critical_fuel_bypasses_suppression() -> None:
    workload = WorkloadMonitor()
    manager = SpeechSuppressionManager(workload)
    _busy(workload)
    fuel = _event(TriggerType.FUEL, risk_level=FuelRiskLevel.CRITICAL.value)

    released = manager.accept_trigger(fuel, now=1.0)

    assert released == (fuel,)


def test_drains_deferred_trigger_when_workload_drops() -> None:
    workload = WorkloadMonitor(
        WorkloadConfig(braking=BrakingConfig(hold_seconds=0.1)),
    )
    manager = SpeechSuppressionManager(workload)
    _busy(workload, now=1.0)
    fuel = _event(TriggerType.FUEL)
    manager.accept_trigger(fuel, now=1.0)
    _idle(workload, now=1.2)
    _idle(workload, now=1.5)

    drained = manager.drain_triggers(now=1.5)

    assert drained == (fuel,)
