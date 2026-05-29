from dataclasses import dataclass
from typing import Any


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

    @property
    def warnings(self) -> tuple[str, ...]:
        messages: list[str] = []
        if self.missing_required:
            messages.append(
                "Missing required SDK variables: "
                + ", ".join(self.missing_required)
            )
        if self.missing_optional:
            messages.append(
                "Missing optional SDK variables: "
                + ", ".join(self.missing_optional)
            )
        return tuple(messages)

    def as_dict(self) -> dict[str, Any]:
        return {
            "available_count": len(self.available),
            "missing_required": list(self.missing_required),
            "missing_optional": list(self.missing_optional),
            "warnings": list(self.warnings),
        }
