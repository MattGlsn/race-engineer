from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VariableAvailabilityReport:
    """Comparison of required and optional variables against the SDK."""

    available: frozenset[str]
    missing_required: tuple[str, ...]
    missing_optional: tuple[str, ...]

    @property
    def has_missing_required(self) -> bool:
        return bool(self.missing_required)

    @property
    def has_missing_optional(self) -> bool:
        return bool(self.missing_optional)

    @property
    def is_fully_available(self) -> bool:
        return not self.has_missing_required and not self.has_missing_optional
