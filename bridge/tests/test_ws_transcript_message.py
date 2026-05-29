from race_engineer.api.ws.messages import build_transcript_message


def test_build_transcript_message_shape() -> None:
    message = build_transcript_message(role="driver", text="pit this lap")

    assert message["type"] == "transcript"
    assert isinstance(message["ts"], float)
    assert message["data"]["role"] == "driver"
    assert message["data"]["text"] == "pit this lap"
