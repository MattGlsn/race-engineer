from race_engineer.proactive.suppression.workload import WorkloadConfig, WorkloadMonitor
from race_engineer.telemetry.models import TelemetrySnapshot


def _snapshot(
    *,
    brake: float | None = None,
    steering: float | None = None,
    speed: float | None = 30.0,
) -> TelemetrySnapshot:
    return TelemetrySnapshot(brake=brake, steering=steering, speed=speed)


def test_high_workload_when_braking_at_speed() -> None:
    monitor = WorkloadMonitor()

    assert monitor.observe(_snapshot(brake=0.25), now=0.0) is True
    assert monitor.should_suppress() is True


def test_not_high_workload_when_braking_below_min_speed() -> None:
    monitor = WorkloadMonitor(WorkloadConfig(min_speed_mps=5.0))

    assert monitor.observe(_snapshot(brake=0.9, speed=2.0), now=0.0) is False


def test_high_workload_on_steering_rate() -> None:
    monitor = WorkloadMonitor(
        WorkloadConfig(steering_rate_rad_per_s=1.0, steering_busy_rad=2.0),
    )
    monitor.observe(_snapshot(brake=0.0, steering=0.0), now=0.0)

    assert monitor.observe(_snapshot(brake=0.0, steering=0.5), now=0.2) is True


def test_reset_clears_workload() -> None:
    monitor = WorkloadMonitor()
    monitor.observe(_snapshot(brake=0.5), now=0.0)

    monitor.reset()

    assert monitor.should_suppress() is False
