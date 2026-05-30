from race_engineer.api.ws.messages import build_proactive_trigger_message
from race_engineer.proactive.triggers.models import TriggerEvent, TriggerType


def test_build_proactive_trigger_message() -> None:
    message = build_proactive_trigger_message(
        TriggerEvent(
            type=TriggerType.FUEL,
            payload={"risk_level": "caution"},
        ),
    )

    assert message["type"] == "proactive_trigger"
    assert message["data"]["trigger"] == "fuel"
    assert message["data"]["payload"] == {"risk_level": "caution"}
    assert "ts" in message
