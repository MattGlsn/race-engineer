import asyncio
from unittest.mock import AsyncMock, MagicMock

from race_engineer.voice.hotkey.binding import HotkeyBinding
from race_engineer.voice.hotkey.config import VoiceHotkeyConfig
from race_engineer.voice.hotkey.service import VoiceHotkeyService
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult


def test_service_broadcasts_successful_transcript() -> None:
    pipeline = MagicMock()
    manager = MagicMock()
    manager.broadcast = AsyncMock()
    listener = MagicMock()
    config = VoiceHotkeyConfig(binding=HotkeyBinding.parse("ctrl+shift+space"))
    service = VoiceHotkeyService(
        pipeline,
        manager,
        config=config,
        listener=listener,
    )
    loop = asyncio.new_event_loop()
    service.start(loop)

    result = VoicePipelineResult.ok(
        TranscriptResult(text="box now", language_code="en", duration_ms=50)
    )
    service._on_transcript(result)
    loop.run_until_complete(asyncio.sleep(0))
    loop.close()

    manager.broadcast.assert_called_once()
    message = manager.broadcast.call_args.args[0]
    assert message["type"] == "transcript"
    assert message["data"]["role"] == "driver"
    assert message["data"]["text"] == "box now"
    assert message["data"]["intent"] == "unknown"
