from race_engineer.fuel.models import FuelConsumptionSnapshot
from race_engineer.fuel.projection.finish import calculate_finish_fuel
from race_engineer.fuel.projection.models import FuelProjectionSnapshot
from race_engineer.fuel.projection.risk import classify_fuel_risk, fuel_warning_active
from race_engineer.fuel.projection.session_laps import SessionLapsReader


class FuelProjectionEngine:
    """Projects finish fuel and risk from live fuel and consumption metrics."""

    def __init__(self, session_laps_reader: SessionLapsReader | None = None) -> None:
        self._session_laps_reader = (
            session_laps_reader
            if session_laps_reader is not None
            else SessionLapsReader()
        )

    def project(
        self,
        fuel_level: float | None,
        consumption: FuelConsumptionSnapshot,
    ) -> FuelProjectionSnapshot:
        laps_remaining = self._session_laps_reader.read_laps_remaining()
        projected_finish_fuel = calculate_finish_fuel(
            fuel_level,
            laps_remaining,
            consumption.rolling_avg_usage,
        )
        risk_level = classify_fuel_risk(
            projected_finish_fuel,
            consumption.rolling_avg_usage,
        )

        return FuelProjectionSnapshot(
            laps_remaining=laps_remaining,
            projected_finish_fuel=projected_finish_fuel,
            risk_level=risk_level,
            warning=fuel_warning_active(risk_level),
        )
