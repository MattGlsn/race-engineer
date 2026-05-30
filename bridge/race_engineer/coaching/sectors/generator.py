from race_engineer.coaching.sectors.models import LapSectors, Sector
from race_engineer.coaching.trace.models import LapTrace

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

    sector_width = 1.0 / sector_count
    sectors = tuple(
        Sector(
            index=index,
            start_dist_pct=index * sector_width,
            end_dist_pct=(index + 1) * sector_width,
        )
        for index in range(sector_count)
    )
    return LapSectors(lap=lap_trace.lap, sectors=sectors)
