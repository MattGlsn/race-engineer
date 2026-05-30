from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SectorLoss:
    """Time delta for one sector versus a reference lap."""

    index: int
    start_dist_pct: float
    end_dist_pct: float
    loss_seconds: float


@dataclass(frozen=True, slots=True)
class LapDelta:
    """Sector-by-sector comparison of a lap against a reference lap."""

    current_lap: int
    reference_lap: int
    reference_kind: str
    total_loss_seconds: float
    sector_losses: tuple[SectorLoss, ...]
