from race_engineer.context.models import AnalyticsContextState, LapFuelSummary
from race_engineer.fuel.models import FuelConsumptionSnapshot
from race_engineer.storage.fuel_repository import FuelLapRepository

DEFAULT_RECENT_LAP_LIMIT = 5


def build_analytics_state(
    fuel_consumption: FuelConsumptionSnapshot,
    *,
    repository: FuelLapRepository | None = None,
    session_key: str | None = None,
    recent_lap_limit: int = DEFAULT_RECENT_LAP_LIMIT,
) -> AnalyticsContextState:
    """Build fuel analytics context from tracker snapshot and optional lap history."""
    recent_lap_fuel: tuple[LapFuelSummary, ...] = ()
    if repository is not None and session_key is not None:
        records = repository.list_for_session(session_key)
        recent_lap_fuel = tuple(
            LapFuelSummary(lap=record.lap, usage_liters=record.usage_liters)
            for record in records[-recent_lap_limit:]
        )

    return AnalyticsContextState(
        valid_lap_count=fuel_consumption.valid_lap_count,
        rolling_avg_usage=fuel_consumption.rolling_avg_usage,
        last_lap_usage=fuel_consumption.last_lap_usage,
        recent_lap_fuel=recent_lap_fuel,
    )
