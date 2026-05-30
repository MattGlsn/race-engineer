from race_engineer.coaching.sectors.models import LapSectors, Sector
from race_engineer.coaching.trace.models import LapTrace, TraceSample

DEFAULT_SECTOR_COUNT = 50


def generate_sectors(
    lap_trace: LapTrace,
    *,
    sector_count: int = DEFAULT_SECTOR_COUNT,
) -> LapSectors:
    """Divide a lap trace into equal distance sectors."""
    if sector_count < 1:
        raise ValueError("sector_count must be positive")
    if not lap_trace.samples:
        raise ValueError("lap trace has no samples")

    samples = _sorted_samples(lap_trace.samples)
    sector_width = 1.0 / sector_count
    sectors = tuple(
        _build_sector(
            samples,
            index=index,
            start=index * sector_width,
            end=(index + 1) * sector_width,
            is_last=index == sector_count - 1,
        )
        for index in range(sector_count)
    )
    return LapSectors(lap=lap_trace.lap, sectors=sectors)


def _build_sector(
    samples: tuple[TraceSample, ...],
    *,
    index: int,
    start: float,
    end: float,
    is_last: bool,
) -> Sector:
    start_ts = _interpolate_timestamp(samples, start)
    end_ts = _interpolate_timestamp(samples, end)
    return Sector(
        index=index,
        start_dist_pct=start,
        end_dist_pct=end,
        avg_speed=_sector_avg_speed(samples, start, end, is_last=is_last),
        duration_seconds=max(end_ts - start_ts, 0.0),
    )


def _sorted_samples(samples: tuple[TraceSample, ...]) -> tuple[TraceSample, ...]:
    return tuple(sorted(samples, key=lambda sample: (sample.lap_dist_pct, sample.timestamp)))


def _interpolate_field(
    samples: tuple[TraceSample, ...],
    dist_pct: float,
    field: str,
) -> float:
    if dist_pct <= samples[0].lap_dist_pct:
        return float(getattr(samples[0], field))
    if dist_pct >= samples[-1].lap_dist_pct:
        return float(getattr(samples[-1], field))

    for index in range(len(samples) - 1):
        left = samples[index]
        right = samples[index + 1]
        if left.lap_dist_pct <= dist_pct <= right.lap_dist_pct:
            if right.lap_dist_pct == left.lap_dist_pct:
                return float(getattr(left, field))
            ratio = (dist_pct - left.lap_dist_pct) / (
                right.lap_dist_pct - left.lap_dist_pct
            )
            left_value = float(getattr(left, field))
            right_value = float(getattr(right, field))
            return left_value + ratio * (right_value - left_value)

    return float(getattr(samples[-1], field))


def _interpolate_speed(samples: tuple[TraceSample, ...], dist_pct: float) -> float:
    return _interpolate_field(samples, dist_pct, "speed")


def _interpolate_timestamp(
    samples: tuple[TraceSample, ...],
    dist_pct: float,
) -> float:
    return _interpolate_field(samples, dist_pct, "timestamp")


def _sector_avg_speed(
    samples: tuple[TraceSample, ...],
    start: float,
    end: float,
    *,
    is_last: bool,
) -> float:
    in_sector = [
        sample
        for sample in samples
        if _sector_contains(sample.lap_dist_pct, start, end, is_last=is_last)
    ]
    if in_sector:
        return sum(sample.speed for sample in in_sector) / len(in_sector)

    return _interpolate_speed(samples, (start + end) / 2)


def _sector_contains(
    dist_pct: float,
    start: float,
    end: float,
    *,
    is_last: bool,
) -> bool:
    if dist_pct < start:
        return False
    if is_last:
        return dist_pct <= end
    return dist_pct < end
