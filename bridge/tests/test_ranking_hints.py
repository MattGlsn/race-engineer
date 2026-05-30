from race_engineer.coaching.delta.models import SectorLoss
from race_engineer.coaching.ranking import generate_coaching_hint
from race_engineer.coaching.trace.models import LapTrace, TraceSample


def _sector_loss(*, index: int = 12) -> SectorLoss:
    sector_width = 1.0 / 50
    start = index * sector_width
    end = (index + 1) * sector_width
    return SectorLoss(
        index=index,
        start_dist_pct=start,
        end_dist_pct=end,
        loss_seconds=0.05,
    )


def _trace_for_sector(
    *,
    lap: int,
    index: int,
    speed: float,
    brake: float = 0.0,
    throttle: float = 0.8,
) -> LapTrace:
    sector_width = 1.0 / 50
    start = index * sector_width
    mid = start + sector_width / 2
    end = (index + 1) * sector_width
    samples = tuple(
        TraceSample(
            timestamp=dist * 100.0,
            lap_dist_pct=dist,
            speed=speed,
            fuel=30.0,
            gear=3,
            throttle=throttle,
            brake=brake,
            steering=0.0,
            rpm=6000.0,
        )
        for dist in (start, mid, end)
    )
    return LapTrace(lap=lap, samples=samples)


def test_coaching_hint_suggests_more_minimum_speed() -> None:
    sector = _sector_loss()
    current = _trace_for_sector(lap=2, index=12, speed=130.0)
    reference = _trace_for_sector(lap=1, index=12, speed=140.0)

    hint = generate_coaching_hint(sector, current, reference)

    assert "minimum speed" in hint.lower()


def test_coaching_hint_suggests_easing_brakes() -> None:
    sector = _sector_loss()
    current = _trace_for_sector(lap=2, index=12, speed=140.0, brake=0.4)
    reference = _trace_for_sector(lap=1, index=12, speed=140.0, brake=0.1)

    hint = generate_coaching_hint(sector, current, reference)

    assert "brake" in hint.lower()


def test_coaching_hint_suggests_earlier_throttle() -> None:
    sector = _sector_loss()
    current = _trace_for_sector(lap=2, index=12, speed=140.0, throttle=0.5)
    reference = _trace_for_sector(lap=1, index=12, speed=140.0, throttle=0.9)

    hint = generate_coaching_hint(sector, current, reference)

    assert "throttle" in hint.lower()


def test_coaching_hint_falls_back_when_traces_match() -> None:
    sector = _sector_loss()
    trace = _trace_for_sector(lap=2, index=12, speed=140.0)

    hint = generate_coaching_hint(sector, trace, trace)

    assert "matching pace" in hint.lower()
