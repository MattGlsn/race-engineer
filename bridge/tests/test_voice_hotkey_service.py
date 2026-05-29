import asyncio
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from race_engineer.voice.hotkey.binding import HotkeyBinding
from race_engineer.voice.hotkey.config import VoiceHotkeyConfig
from race_engineer.voice.hotkey.service import VoiceHotkeyService
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult


def test_service_delegates_successful_transcript_to_orchestrator() -> None:
    pipeline = MagicMock()
    listener = MagicMock()
    orchestrator = MagicMock()
    config = VoiceHotkeyConfig(binding=HotkeyBinding.parse("ctrl+shift+space"))
    executor = ThreadPoolExecutor(max_workers=1)
    service = VoiceHotkeyService(
        pipeline,
        config=config,
        listener=listener,
        orchestrator=orchestrator,
        executor=executor,
    )
    loop = asyncio.new_event_loop()
    service.start(loop)

    result = VoicePipelineResult.ok(
        TranscriptResult(text="how much fuel?", language_code="en", duration_ms=50)
    )
    service._on_transcript(result)
    executor.shutdown(wait=True)
    loop.close()

    orchestrator.handle_transcript.assert_called_once_with(
        text="how much fuel?",
        intent="fuel",
    )
