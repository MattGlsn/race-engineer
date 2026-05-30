from race_engineer.coaching.delta.calculator import top_losses
from race_engineer.coaching.delta.models import LapDelta, SectorLoss
from race_engineer.coaching.ranking.explanations import generate_explanation
from race_engineer.coaching.ranking.hints import generate_coaching_hint
from race_engineer.coaching.ranking.models import RankedLoss, TimeLossRanking
from race_engineer.coaching.trace.models import LapTrace

DEFAULT_RANKING_LIMIT = 3


def format_corner_reference(sector_loss: SectorLoss) -> str:
    """Return a track-position reference for one sector loss."""
    sector_number = sector_loss.index + 1
    start_pct = _format_lap_percent(sector_loss.start_dist_pct)
    end_pct = _format_lap_percent(sector_loss.end_dist_pct)
    return f"sector {sector_number} ({start_pct}–{end_pct} of lap)"


def build_time_loss_ranking(
    lap_delta: LapDelta,
    *,
    current: LapTrace,
    reference: LapTrace,
    limit: int = DEFAULT_RANKING_LIMIT,
) -> TimeLossRanking:
    """Build a ranked top-N time-loss report for one lap comparison."""
    ranked_losses = tuple(
        RankedLoss(
            rank=rank,
            sector_loss=sector_loss,
            corner_reference=format_corner_reference(sector_loss),
            explanation=generate_explanation(sector_loss),
            hint=generate_coaching_hint(sector_loss, current, reference),
        )
        for rank, sector_loss in enumerate(top_losses(lap_delta, limit=limit), start=1)
    )
    return TimeLossRanking(
        current_lap=lap_delta.current_lap,
        reference_lap=lap_delta.reference_lap,
        reference_kind=lap_delta.reference_kind,
        losses=ranked_losses,
    )


def _format_lap_percent(dist_pct: float) -> str:
    return f"{dist_pct * 100:.0f}%"
