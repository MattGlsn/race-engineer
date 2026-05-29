from race_engineer.availability.models import VariableAvailabilityReport
from race_engineer.availability.requirements import (
    OPTIONAL_VARIABLES,
    REQUIRED_VARIABLES,
)


class VariableAvailabilityChecker:
    """Compares configured variable requirements against SDK availability."""

    def check(self, available: frozenset[str]) -> VariableAvailabilityReport:
        missing_required = tuple(
            name for name in REQUIRED_VARIABLES if name not in available
        )
        missing_optional = tuple(
            name for name in OPTIONAL_VARIABLES if name not in available
        )
        return VariableAvailabilityReport(
            available=available,
            missing_required=missing_required,
            missing_optional=missing_optional,
        )
