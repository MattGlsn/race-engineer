from race_engineer.ai.prompt.safety import SAFETY_RULES


def test_safety_rules_require_grounded_context() -> None:
    lowered = SAFETY_RULES.lower()
    assert "race context json" in lowered
    assert "never invent" in lowered or "do not invent" in lowered


def test_safety_rules_handle_missing_data() -> None:
    lowered = SAFETY_RULES.lower()
    assert "null" in lowered or "missing" in lowered
    assert "disconnected" in lowered


def test_safety_rules_forbid_raw_telemetry() -> None:
    lowered = SAFETY_RULES.lower()
    for term in ("throttle", "brake", "steering", "rpm"):
        assert term in lowered
