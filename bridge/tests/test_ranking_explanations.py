from race_engineer.coaching.delta.models import SectorLoss
from race_engineer.coaching.ranking.explanations import generate_explanation


def _sector_loss(*, index: int = 12, loss_seconds: float = 0.042) -> SectorLoss:
    sector_width = 1.0 / 50
    start = index * sector_width
    end = (index + 1) * sector_width
    return SectorLoss(
        index=index,
        start_dist_pct=start,
        end_dist_pct=end,
        loss_seconds=loss_seconds,
    )


def test_explanation_includes_quantified_loss() -> None:
    explanation = generate_explanation(_sector_loss(loss_seconds=0.042))

    assert "Lost 0.042s" in explanation


def test_explanation_includes_corner_reference() -> None:
    explanation = generate_explanation(_sector_loss(index=12))

    assert "sector 13" in explanation
    assert "24%–26% of lap" in explanation


def test_explanation_trims_trailing_zeros() -> None:
    explanation = generate_explanation(_sector_loss(loss_seconds=0.1))

    assert "Lost 0.1s" in explanation
    assert "0.100" not in explanation
