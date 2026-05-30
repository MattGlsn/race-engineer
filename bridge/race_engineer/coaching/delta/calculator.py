from race_engineer.coaching.delta.models import LapDelta, SectorLoss
from race_engineer.coaching.sectors.models import LapSectors
from race_engineer.coaching.sectors.generator import generate_sectors
from race_engineer.coaching.trace.models import LapTrace

LOSS_SECONDS_PRECISION = 3


def compute_lap_delta(
    current: LapSectors,
    reference: LapSectors,
    *,
    reference_kind: str = "reference",
) -> LapDelta:
    """Compare sector timings and return per-sector losses."""
    if len(current.sectors) != len(reference.sectors):
        raise ValueError("sector count mismatch")

    sector_losses: list[SectorLoss] = []
    total_loss = 0.0
    for current_sector, reference_sector in zip(current.sectors, reference.sectors):
        if current_sector.index != reference_sector.index:
            raise ValueError("sector index mismatch")

        current_duration = current_sector.duration_seconds or 0.0
        reference_duration = reference_sector.duration_seconds or 0.0
        loss = round(current_duration - reference_duration, LOSS_SECONDS_PRECISION)
        sector_losses.append(
            SectorLoss(
                index=current_sector.index,
                start_dist_pct=current_sector.start_dist_pct,
                end_dist_pct=current_sector.end_dist_pct,
                loss_seconds=loss,
            )
        )
        if loss > 0:
            total_loss += loss

    return LapDelta(
        current_lap=current.lap,
        reference_lap=reference.lap,
        reference_kind=reference_kind,
        total_loss_seconds=round(total_loss, LOSS_SECONDS_PRECISION),
        sector_losses=tuple(sector_losses),
    )


def top_losses(lap_delta: LapDelta, *, limit: int = 3) -> tuple[SectorLoss, ...]:
    """Return the largest positive sector losses, sorted descending."""
    if limit < 1:
        raise ValueError("limit must be positive")

    ranked = sorted(
        (sector for sector in lap_delta.sector_losses if sector.loss_seconds > 0),
        key=lambda sector: sector.loss_seconds,
        reverse=True,
    )
    return tuple(ranked[:limit])


def compare_to_previous_lap(current: LapTrace, previous: LapTrace) -> LapDelta:
    """Compare the current lap against the immediately previous lap."""
    if previous.lap != current.lap - 1:
        raise ValueError("previous lap number must be one less than current lap")

    return compute_lap_delta(
        generate_sectors(current),
        generate_sectors(previous),
        reference_kind="previous",
    )
