from race_engineer.coaching.delta.models import SectorLoss
from race_engineer.coaching.sectors import DEFAULT_SECTOR_COUNT
from race_engineer.coaching.trace.models import LapTrace, TraceSample

SPEED_DELTA_THRESHOLD = 2.0
BRAKE_DELTA_THRESHOLD = 0.05
THROTTLE_DELTA_THRESHOLD = 0.05


def generate_coaching_hint(
    sector_loss: SectorLoss,
    current: LapTrace,
    reference: LapTrace,
) -> str:
    """Return a rule-based coaching hint for one loss sector."""
    current_samples = _samples_in_sector(current.samples, sector_loss)
    reference_samples = _samples_in_sector(reference.samples, sector_loss)
    if not current_samples or not reference_samples:
        return "Focus on matching pace through this section."

    current_speed = _avg_field(current_samples, "speed")
    reference_speed = _avg_field(reference_samples, "speed")
    current_brake = _avg_field(current_samples, "brake")
    reference_brake = _avg_field(reference_samples, "brake")
    current_throttle = _avg_field(current_samples, "throttle")
    reference_throttle = _avg_field(reference_samples, "throttle")

    if reference_speed - current_speed >= SPEED_DELTA_THRESHOLD:
        return "Carry more minimum speed through this section."

    if current_brake - reference_brake >= BRAKE_DELTA_THRESHOLD:
        return "Ease off the brakes earlier to carry more entry speed."

    if reference_throttle - current_throttle >= THROTTLE_DELTA_THRESHOLD:
        return "Commit to throttle earlier on exit."

    return "Focus on matching pace through this section."


def _samples_in_sector(
    samples: tuple[TraceSample, ...],
    sector_loss: SectorLoss,
) -> tuple[TraceSample, ...]:
    is_last = sector_loss.index == DEFAULT_SECTOR_COUNT - 1
    return tuple(
        sample
        for sample in samples
        if _sector_contains(
            sample.lap_dist_pct,
            sector_loss.start_dist_pct,
            sector_loss.end_dist_pct,
            is_last=is_last,
        )
    )


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


def _avg_field(samples: tuple[TraceSample, ...], field: str) -> float:
    values = [float(getattr(sample, field)) for sample in samples]
    return sum(values) / len(values)
