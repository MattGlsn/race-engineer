import asyncio
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch

from race_engineer.settings.hotkey import VoiceHotkeySettings
from race_engineer.voice.hotkey.binding import HotkeyBinding
from race_engineer.voice.hotkey.service import VoiceHotkeyService
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult


def test_service_delegates_successful_transcript_to_orchestrator() -> None:
    pipeline = MagicMock()
    listener = MagicMock()
    orchestrator = MagicMock()
    hotkey_settings = VoiceHotkeySettings(HotkeyBinding.parse("ctrl+shift+space"))
    executor = ThreadPoolExecutor(max_workers=1)
    service = VoiceHotkeyService(
        pipeline,
        hotkey_settings=hotkey_settings,
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


@patch("race_engineer.voice.hotkey.service.GlobalHotkeyListener")
def test_rebind_restarts_listener_with_updated_binding(
    mock_listener_cls: MagicMock,
) -> None:
    pipeline = MagicMock()
    orchestrator = MagicMock()
    mock_listener = MagicMock()
    mock_listener_cls.return_value = mock_listener
    hotkey_settings = VoiceHotkeySettings(HotkeyBinding.parse("ctrl+shift+space"))
    executor = ThreadPoolExecutor(max_workers=1)
    service = VoiceHotkeyService(
        pipeline,
        hotkey_settings=hotkey_settings,
        orchestrator=orchestrator,
        executor=executor,
    )
    loop = asyncio.new_event_loop()
    service.start(loop)

    hotkey_settings.set_binding(HotkeyBinding.parse("ctrl+alt+v"))
    service.rebind()

    mock_listener.stop.assert_called_once()
    assert mock_listener_cls.call_count == 2
    latest_binding = mock_listener_cls.call_args_list[-1][0][0]
    assert latest_binding.key == "v"
    assert latest_binding.modifiers == frozenset({"ctrl", "alt"})

    service.stop()
    executor.shutdown(wait=True)
    loop.close()
