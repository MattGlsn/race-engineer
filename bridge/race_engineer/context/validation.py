from collections.abc import Mapping
from typing import Any

from race_engineer.context.models import EngineerContext

MAX_CONTEXT_BYTES = 10 * 1024

FORBIDDEN_TELEMETRY_KEYS = frozenset(
    {
        "throttle",
        "brake",
        "steering",
        "rpm",
        "speed",
        "lap_dist_pct",
        "gear",
    }
)


def serialize_context(context: EngineerContext) -> str:
    """Serialize validated engineer context to compact JSON."""
    return context.model_dump_json(exclude_none=True)


def validate_context_size(payload: str, *, max_bytes: int = MAX_CONTEXT_BYTES) -> None:
    """Raise ValueError when serialized context exceeds the byte budget."""
    if len(payload.encode("utf-8")) > max_bytes:
        raise ValueError(
            f"context payload exceeds {max_bytes} bytes "
            f"({len(payload.encode('utf-8'))} bytes)",
        )


def assert_no_raw_telemetry(payload: Mapping[str, Any] | list[Any]) -> None:
    """Raise ValueError when raw telemetry keys appear in the context payload."""
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if key in FORBIDDEN_TELEMETRY_KEYS:
                raise ValueError(f"context contains forbidden telemetry key: {key}")
            assert_no_raw_telemetry(value)
        return

    if isinstance(payload, list):
        for item in payload:
            assert_no_raw_telemetry(item)


def validate_engineer_context(context: EngineerContext) -> str:
    """Validate schema constraints and return serialized JSON payload."""
    payload = serialize_context(context)
    validate_context_size(payload)
    assert_no_raw_telemetry(context.model_dump(mode="json", exclude_none=True))
    return payload
