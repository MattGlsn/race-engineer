from race_engineer.coaching.delta.models import SectorLoss

LOSS_SECONDS_PRECISION = 3


def generate_explanation(sector_loss: SectorLoss) -> str:
    """Return a human-readable explanation for one sector time loss."""
    loss = format_loss_seconds(sector_loss.loss_seconds)
    start_pct = _format_lap_percent(sector_loss.start_dist_pct)
    end_pct = _format_lap_percent(sector_loss.end_dist_pct)
    sector_number = sector_loss.index + 1
    return (
        f"Lost {loss}s at sector {sector_number} "
        f"({start_pct}–{end_pct} of lap)."
    )


def format_loss_seconds(loss_seconds: float) -> str:
    """Format a loss value with fixed precision, trimming trailing zeros."""
    formatted = f"{loss_seconds:.{LOSS_SECONDS_PRECISION}f}".rstrip("0").rstrip(".")
    if formatted == "-0":
        return "0"
    return formatted


def _format_lap_percent(dist_pct: float) -> str:
    return f"{dist_pct * 100:.0f}%"
