import pytest

from race_engineer.coaching.delta import compute_lap_delta, compare_to_previous_lap, top_losses
from race_engineer.coaching.sectors import generate_sectors
from race_engineer.coaching.trace.models import LapTrace, TraceSample


def _linear_lap_trace(*, lap: int, duration: float = 100.0) -> LapTrace:
    samples = tuple(
        TraceSample(
            timestamp=dist * duration,
            lap_dist_pct=dist,
            speed=150.0,
            fuel=30.0,
            gear=3,
            throttle=0.8,
            brake=0.0,
            steering=0.0,
            rpm=6000.0,
        )
        for dist in (0.0, 0.25, 0.5, 0.75, 1.0)
    )
    return LapTrace(lap=lap, samples=samples)


def _slower_middle_lap_trace(*, lap: int) -> LapTrace:
    samples = tuple(
        TraceSample(
            timestamp=timestamp,
            lap_dist_pct=dist,
            speed=150.0,
            fuel=30.0,
            gear=3,
            throttle=0.8,
            brake=0.0,
            steering=0.0,
            rpm=6000.0,
        )
        for dist, timestamp in (
            (0.0, 0.0),
            (0.25, 25.0),
            (0.5, 60.0),
            (0.75, 85.0),
            (1.0, 110.0),
        )
    )
    return LapTrace(lap=lap, samples=samples)


def test_compute_lap_delta_reports_zero_loss_for_identical_laps() -> None:
    reference = generate_sectors(_linear_lap_trace(lap=1))
    current = generate_sectors(_linear_lap_trace(lap=2))

    result = compute_lap_delta(current, reference)

    assert result.current_lap == 2
    assert result.reference_lap == 1
    assert result.total_loss_seconds == pytest.approx(0.0)
    assert all(sector.loss_seconds == pytest.approx(0.0) for sector in result.sector_losses)


def test_compute_lap_delta_sums_positive_sector_losses() -> None:
    reference = generate_sectors(_linear_lap_trace(lap=1, duration=100.0))
    current = generate_sectors(_slower_middle_lap_trace(lap=2))

    result = compute_lap_delta(current, reference)

    assert result.total_loss_seconds == pytest.approx(10.0)
    assert any(sector.loss_seconds > 0 for sector in result.sector_losses)


def test_top_losses_returns_largest_positive_sectors() -> None:
    reference = generate_sectors(_linear_lap_trace(lap=1, duration=100.0))
    current = generate_sectors(_slower_middle_lap_trace(lap=2))
    lap_delta = compute_lap_delta(current, reference)

    losses = top_losses(lap_delta, limit=3)

    assert len(losses) == 3
    assert losses[0].loss_seconds >= losses[1].loss_seconds >= losses[2].loss_seconds
    assert all(sector.loss_seconds > 0 for sector in losses)


def test_compute_lap_delta_is_repeatable() -> None:
    reference = generate_sectors(_linear_lap_trace(lap=1))
    current = generate_sectors(_slower_middle_lap_trace(lap=2))

    first = compute_lap_delta(current, reference)
    second = compute_lap_delta(current, reference)

    assert first == second


def test_compute_lap_delta_rejects_sector_count_mismatch() -> None:
    reference = generate_sectors(_linear_lap_trace(lap=1))
    current = generate_sectors(_linear_lap_trace(lap=2), sector_count=25)

    with pytest.raises(ValueError, match="sector count mismatch"):
        compute_lap_delta(current, reference)


def test_compare_to_previous_lap_uses_previous_lap_reference() -> None:
    previous = _linear_lap_trace(lap=1, duration=100.0)
    current = _slower_middle_lap_trace(lap=2)

    result = compare_to_previous_lap(current, previous)

    assert result.reference_kind == "previous"
    assert result.reference_lap == 1
    assert result.current_lap == 2
    assert result.total_loss_seconds == pytest.approx(10.0)


def test_compare_to_previous_lap_rejects_non_consecutive_laps() -> None:
    with pytest.raises(ValueError, match="previous lap number"):
        compare_to_previous_lap(
            _linear_lap_trace(lap=3),
            _linear_lap_trace(lap=1),
        )
