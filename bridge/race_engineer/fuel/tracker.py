from race_engineer.fuel.models import FuelConsumptionSnapshot, LapFuelRecord
from race_engineer.fuel.usage import calculate_lap_usage
from race_engineer.storage.fuel_repository import FuelLapRepository


def build_session_key(track_name: str | None, session_type: str | None) -> str:
    track = track_name or "unknown"
    session = session_type or "unknown"
    return f"{track}|{session}"


class FuelConsumptionTracker:
    """Tracks fuel at lap boundaries and persists completed lap records."""

    def __init__(self, repository: FuelLapRepository | None = None) -> None:
        self._repository = repository
        self._session_key: str | None = None
        self._last_lap_completed: int | None = None
        self._fuel_at_lap_start: float | None = None
        self._valid_usages: list[float] = []
        self._snapshot = FuelConsumptionSnapshot()

    @property
    def session_key(self) -> str | None:
        return self._session_key

    @property
    def snapshot(self) -> FuelConsumptionSnapshot:
        return self._snapshot

    def begin_session(self, session_key: str) -> None:
        self.reset()
        self._session_key = session_key

    def reset(self) -> None:
        self._session_key = None
        self._last_lap_completed = None
        self._fuel_at_lap_start = None
        self._valid_usages = []
        self._snapshot = FuelConsumptionSnapshot()

    def update(
        self,
        fuel_level: float | None,
        laps_completed: int | None,
    ) -> FuelConsumptionSnapshot:
        if self._session_key is None:
            return self._snapshot

        if fuel_level is None or laps_completed is None or laps_completed < 0:
            return self._snapshot

        if self._last_lap_completed is None:
            self._last_lap_completed = laps_completed
            self._fuel_at_lap_start = fuel_level
            self._snapshot = FuelConsumptionSnapshot(fuel_at_lap_start=fuel_level)
            return self._snapshot

        if laps_completed < self._last_lap_completed:
            self._last_lap_completed = laps_completed
            self._fuel_at_lap_start = fuel_level
            self._valid_usages = []
            self._snapshot = FuelConsumptionSnapshot(fuel_at_lap_start=fuel_level)
            return self._snapshot

        if laps_completed > self._last_lap_completed:
            self._complete_lap(laps_completed, fuel_level)

        self._snapshot = FuelConsumptionSnapshot(
            last_lap=self._last_lap_completed,
            last_lap_usage=self._valid_usages[-1] if self._valid_usages else None,
            rolling_avg_usage=self._mean_usage(),
            valid_lap_count=len(self._valid_usages),
            fuel_at_lap_start=self._fuel_at_lap_start,
        )
        return self._snapshot

    def _complete_lap(self, lap: int, fuel_end: float) -> None:
        fuel_start = self._fuel_at_lap_start
        usage = calculate_lap_usage(fuel_start, fuel_end)
        self._last_lap_completed = lap
        self._fuel_at_lap_start = fuel_end

        if usage is None or self._session_key is None:
            return

        record = LapFuelRecord(
            lap=lap,
            fuel_start=fuel_start if fuel_start is not None else fuel_end,
            fuel_end=fuel_end,
            usage_liters=usage,
        )
        if self._repository is not None:
            self._repository.save(self._session_key, record)

        self._valid_usages.append(usage)

    def _mean_usage(self) -> float | None:
        if not self._valid_usages:
            return None
        return round(sum(self._valid_usages) / len(self._valid_usages), 3)
