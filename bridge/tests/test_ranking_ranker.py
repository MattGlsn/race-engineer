import pytest

from race_engineer.coaching.delta import compare_to_previous_lap, compute_lap_delta, top_losses
from race_engineer.coaching.ranking import build_time_loss_ranking, format_corner_reference
from race_engineer.coaching.ranking.models import TimeLossRanking
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
            speed=130.0,
            fuel=30.0,
            gear=3,
            throttle=0.5,
            brake=0.3,
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


def test_build_time_loss_ranking_returns_top_three_losses() -> None:
    previous = _linear_lap_trace(lap=1, duration=100.0)
    current = _slower_middle_lap_trace(lap=2)
    lap_delta = compare_to_previous_lap(current, previous)

    ranking = build_time_loss_ranking(lap_delta, current=current, reference=previous)

    assert isinstance(ranking, TimeLossRanking)
    assert ranking.current_lap == 2
    assert ranking.reference_lap == 1
    assert len(ranking.losses) == 3
    assert ranking.losses[0].rank == 1
    assert ranking.losses[0].sector_loss.loss_seconds >= ranking.losses[1].sector_loss.loss_seconds


def test_ranked_loss_includes_corner_reference_explanation_and_hint() -> None:
    previous = _linear_lap_trace(lap=1, duration=100.0)
    current = _slower_middle_lap_trace(lap=2)
    lap_delta = compare_to_previous_lap(current, previous)

    ranking = build_time_loss_ranking(lap_delta, current=current, reference=previous)
    top_loss = ranking.losses[0]

    assert top_loss.corner_reference.startswith("sector ")
    assert "Lost" in top_loss.explanation
    assert top_loss.hint


def test_format_corner_reference_uses_sector_bounds() -> None:
    reference = generate_sectors(_linear_lap_trace(lap=1))
    current = generate_sectors(_slower_middle_lap_trace(lap=2))
    lap_delta = compute_lap_delta(current, reference)
    sector_loss = top_losses(lap_delta, limit=1)[0]

    corner_reference = format_corner_reference(sector_loss)

    assert corner_reference == (
        f"sector {sector_loss.index + 1} "
        f"({sector_loss.start_dist_pct * 100:.0f}%–{sector_loss.end_dist_pct * 100:.0f}% of lap)"
    )


def test_build_time_loss_ranking_respects_limit() -> None:
    previous = _linear_lap_trace(lap=1, duration=100.0)
    current = _slower_middle_lap_trace(lap=2)
    lap_delta = compare_to_previous_lap(current, previous)

    ranking = build_time_loss_ranking(
        lap_delta,
        current=current,
        reference=previous,
        limit=2,
    )

    assert len(ranking.losses) == 2
