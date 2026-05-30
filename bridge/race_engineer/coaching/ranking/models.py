from dataclasses import dataclass

from race_engineer.coaching.delta.models import LapDelta, SectorLoss


@dataclass(frozen=True, slots=True)
class RankedLoss:
    """One ranked time loss with coaching context."""

    rank: int
    sector_loss: SectorLoss
    corner_reference: str
    explanation: str
    hint: str


@dataclass(frozen=True, slots=True)
class TimeLossRanking:
    """Top time losses for a lap compared against a reference."""

    current_lap: int
    reference_lap: int
    reference_kind: str
    losses: tuple[RankedLoss, ...]
