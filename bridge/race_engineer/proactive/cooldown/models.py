from dataclasses import dataclass

DEFAULT_GLOBAL_INTERVAL_SECONDS = 10.0


@dataclass(frozen=True, slots=True)
class CooldownConfig:
    """Rate-limit settings for proactive trigger broadcasts."""

    global_interval_seconds: float = DEFAULT_GLOBAL_INTERVAL_SECONDS
