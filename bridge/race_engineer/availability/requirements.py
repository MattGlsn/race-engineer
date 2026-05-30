from dataclasses import dataclass
from typing import Any

from race_engineer.gap import variables as gap_vars
from race_engineer.position import variables as position_vars
from race_engineer.proactive.incident import variables as incident_vars
from race_engineer.proactive.lap import variables as lap_vars
from race_engineer.standings import variables as standings_vars
from race_engineer.telemetry import variables as telemetry_vars


@dataclass(frozen=True, slots=True)
class VariableRequirement:
    name: str
    required: bool


def _collect_module_variables(module: Any) -> list[str]:
    return [
        value
        for name, value in vars(module).items()
        if name.isupper() and isinstance(value, str)
    ]


REQUIRED_VARIABLES: tuple[str, ...] = tuple(
    sorted(_collect_module_variables(telemetry_vars)),
)
OPTIONAL_VARIABLES: tuple[str, ...] = tuple(
    sorted(
        set(
            _collect_module_variables(standings_vars)
            + _collect_module_variables(position_vars)
            +             _collect_module_variables(gap_vars)
            + _collect_module_variables(incident_vars)
            + _collect_module_variables(lap_vars),
        ),
    ),
)


def all_variable_requirements() -> tuple[VariableRequirement, ...]:
    return tuple(
        VariableRequirement(name=name, required=True)
        for name in REQUIRED_VARIABLES
    ) + tuple(
        VariableRequirement(name=name, required=False)
        for name in OPTIONAL_VARIABLES
    )
