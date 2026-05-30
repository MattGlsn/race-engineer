import pytest

from race_engineer.coaching.sectors import DEFAULT_SECTOR_COUNT, generate_sectors
from race_engineer.coaching.trace.models import LapTrace, TraceSample


def _sample(index: int, *, count: int = 100) -> TraceSample:
    return TraceSample(
        timestamp=float(index),
        lap_dist_pct=index / count,
        speed=100.0 + index,
        fuel=30.0,
        gear=3,
        throttle=0.8,
        brake=0.0,
        steering=0.0,
        rpm=6000.0,
    )


def _lap_trace(sample_count: int = 100, *, lap: int = 1) -> LapTrace:
    return LapTrace(
        lap=lap,
        samples=tuple(_sample(index, count=sample_count) for index in range(sample_count)),
    )


def test_generate_sectors_divides_lap_into_fifty_sectors() -> None:
    result = generate_sectors(_lap_trace())

    assert result.lap == 1
    assert len(result.sectors) == DEFAULT_SECTOR_COUNT


def test_generate_sectors_use_equal_two_percent_width() -> None:
    result = generate_sectors(_lap_trace())
    sector_width = 1.0 / DEFAULT_SECTOR_COUNT

    for index, sector in enumerate(result.sectors):
        assert sector.index == index
        assert sector.start_dist_pct == pytest.approx(index * sector_width)
        assert sector.end_dist_pct == pytest.approx((index + 1) * sector_width)


def test_generate_sectors_cover_full_lap_distance() -> None:
    result = generate_sectors(_lap_trace())

    assert result.sectors[0].start_dist_pct == pytest.approx(0.0)
    assert result.sectors[-1].end_dist_pct == pytest.approx(1.0)


def test_generate_sectors_rejects_empty_trace() -> None:
    with pytest.raises(ValueError, match="no samples"):
        generate_sectors(LapTrace(lap=1, samples=()))
