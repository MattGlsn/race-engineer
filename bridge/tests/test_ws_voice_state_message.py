from race_engineer.api.ws.messages import build_voice_state_message


def test_build_voice_state_message_shape() -> None:
    message = build_voice_state_message(status="recording")

    assert message["type"] == "voice_state"
    assert message["data"] == {"status": "recording"}
    assert isinstance(message["ts"], float)
