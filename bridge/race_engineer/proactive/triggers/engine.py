from dataclasses import dataclass, field

from race_engineer.proactive.triggers.fastest_lap import evaluate_fastest_lap
from race_engineer.proactive.triggers.fuel import evaluate_fuel
from race_engineer.proactive.triggers.gap import evaluate_gap
from race_engineer.proactive.triggers.incident import evaluate_incident
from race_engineer.proactive.triggers.models import TriggerEvent, TriggerSnapshot
from race_engineer.fuel.projection.models import FuelRiskLevel


@dataclass
class TriggerEngine:
    """Evaluates proactive trigger rules with per-session deduplication."""

    _session_key: str | None = None
    _last_best_lap_time: float | None = None
    _last_incident_count: int | None = None
    _last_fuel_risk_level: FuelRiskLevel = FuelRiskLevel.UNKNOWN
    _gap_ahead_armed: bool = True
    _gap_behind_armed: bool = True
    _events: list[TriggerEvent] = field(default_factory=list)

    def begin_session(self, session_key: str) -> None:
        self.reset()
        self._session_key = session_key

    def reset(self) -> None:
        self._session_key = None
        self._last_best_lap_time = None
        self._last_incident_count = None
        self._last_fuel_risk_level = FuelRiskLevel.UNKNOWN
        self._gap_ahead_armed = True
        self._gap_behind_armed = True

    def evaluate(self, snapshot: TriggerSnapshot) -> tuple[TriggerEvent, ...]:
        if snapshot.session_key != self._session_key:
            if snapshot.session_key is not None:
                self.begin_session(snapshot.session_key)
            else:
                return ()

        events: list[TriggerEvent] = []

        fastest_lap_event, self._last_best_lap_time = evaluate_fastest_lap(
            snapshot,
            last_best_lap_time=self._last_best_lap_time,
        )
        if fastest_lap_event is not None:
            events.append(fastest_lap_event)

        incident_event, self._last_incident_count = evaluate_incident(
            snapshot,
            last_incident_count=self._last_incident_count,
        )
        if incident_event is not None:
            events.append(incident_event)

        fuel_event, self._last_fuel_risk_level = evaluate_fuel(
            snapshot,
            last_risk_level=self._last_fuel_risk_level,
        )
        if fuel_event is not None:
            events.append(fuel_event)

        gap_events, self._gap_ahead_armed, self._gap_behind_armed = evaluate_gap(
            snapshot,
            gap_ahead_armed=self._gap_ahead_armed,
            gap_behind_armed=self._gap_behind_armed,
        )
        events.extend(gap_events)

        return tuple(events)
