from race_engineer.proactive.suppression.braking import BrakingConfig, BrakingZoneTracker
from race_engineer.telemetry.models import TelemetrySnapshot


def _snapshot(*, brake: float | None) -> TelemetrySnapshot:
    return TelemetrySnapshot(brake=brake)


def test_enters_braking_zone_when_brake_crosses_on_threshold() -> None:
    tracker = BrakingZoneTracker(BrakingConfig(on_threshold=0.15, hold_seconds=0.4))

    assert tracker.update(_snapshot(brake=0.0), now=0.0) is False
    assert tracker.update(_snapshot(brake=0.2), now=0.1) is True
    assert tracker.in_braking_zone is True


def test_exits_braking_zone_after_off_threshold_and_hold() -> None:
    tracker = BrakingZoneTracker(
        BrakingConfig(
            on_threshold=0.15,
            off_threshold=0.08,
            hold_seconds=0.4,
        ),
    )
    tracker.update(_snapshot(brake=0.3), now=0.0)

    assert tracker.update(_snapshot(brake=0.05), now=0.1) is True
    assert tracker.update(_snapshot(brake=0.05), now=0.3) is True
    assert tracker.update(_snapshot(brake=0.05), now=0.5) is False


def test_reset_clears_braking_state() -> None:
    tracker = BrakingZoneTracker()
    tracker.update(_snapshot(brake=0.5), now=0.0)

    tracker.reset()

    assert tracker.in_braking_zone is False
