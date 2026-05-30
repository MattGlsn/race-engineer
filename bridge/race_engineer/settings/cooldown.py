from race_engineer.proactive.cooldown.models import (
    CooldownConfig,
    DEFAULT_GLOBAL_INTERVAL_SECONDS,
    DEFAULT_TRIGGER_INTERVALS_SECONDS,
    default_cooldown_config,
)
from race_engineer.proactive.triggers.models import TriggerType


class CooldownSettings:
    """In-memory proactive trigger cooldown preferences shared by API and broadcaster."""

    def __init__(self, config: CooldownConfig | None = None) -> None:
        self._config = config or default_cooldown_config()

    @property
    def config(self) -> CooldownConfig:
        return self._config

    def update(
        self,
        *,
        global_interval_seconds: float | None = None,
        trigger_intervals_seconds: dict[TriggerType, float] | None = None,
    ) -> None:
        intervals = dict(self._config.trigger_intervals_seconds)
        if trigger_intervals_seconds is not None:
            intervals.update(trigger_intervals_seconds)

        self._config = CooldownConfig(
            global_interval_seconds=(
                global_interval_seconds
                if global_interval_seconds is not None
                else self._config.global_interval_seconds
            ),
            trigger_intervals_seconds=intervals,
        )


def validate_cooldown_interval(seconds: float) -> float:
    if seconds < 0:
        raise ValueError("cooldown interval must be non-negative")
    return seconds
