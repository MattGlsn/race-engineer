from dataclasses import dataclass, field

from race_engineer.proactive.triggers.models import TriggerType

DEFAULT_GLOBAL_INTERVAL_SECONDS = 10.0

DEFAULT_TRIGGER_INTERVALS_SECONDS: dict[TriggerType, float] = {
    TriggerType.INCIDENT: 30.0,
    TriggerType.FUEL: 60.0,
    TriggerType.GAP_CLOSING_AHEAD: 45.0,
    TriggerType.GAP_CLOSING_BEHIND: 45.0,
    TriggerType.FASTEST_LAP: 120.0,
}


@dataclass(frozen=True, slots=True)
class CooldownConfig:
    """Rate-limit settings for proactive trigger broadcasts."""

    global_interval_seconds: float = DEFAULT_GLOBAL_INTERVAL_SECONDS
    trigger_intervals_seconds: dict[TriggerType, float] = field(
        default_factory=lambda: dict(DEFAULT_TRIGGER_INTERVALS_SECONDS),
    )

    def interval_for(self, trigger_type: TriggerType) -> float:
        return self.trigger_intervals_seconds.get(
            trigger_type,
            DEFAULT_GLOBAL_INTERVAL_SECONDS,
        )


def default_cooldown_config() -> CooldownConfig:
    return CooldownConfig()
