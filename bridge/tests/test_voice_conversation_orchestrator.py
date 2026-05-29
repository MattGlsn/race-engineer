import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from race_engineer.ai.fallback import LLM_FALLBACK_MESSAGE
from race_engineer.ai.models import EngineerAskResult
from race_engineer.ai.service import EngineerAiService
from race_engineer.context.aggregator import empty_engineer_context
from race_engineer.context.models import EngineerContext, SessionContextState
from race_engineer.context.validation import validate_engineer_context
from race_engineer.ai.prompt.models import PersonalityMode
from race_engineer.settings.personality import PersonalitySettings
from race_engineer.voice.conversation.orchestrator import (
    AI_NOT_CONFIGURED_MESSAGE,
    TTS_NOT_CONFIGURED_MESSAGE,
    VoiceConversationOrchestrator,
)
from race_engineer.voice.engineer import EngineerVoiceService
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.tts.models import SynthesisResult


@pytest.fixture
def context() -> EngineerContext:
    built = EngineerContext(
        session=SessionContextState(track_name="Spa", session_type="Race", field_size=20),
        race=empty_engineer_context().race,
        driver=empty_engineer_context().driver,
        analytics=empty_engineer_context().analytics,
    )
    validate_engineer_context(built)
    return built


@pytest.fixture
def ws_manager() -> MagicMock:
    manager = MagicMock()
    manager.broadcast = AsyncMock()
    return manager


@pytest.fixture
def context_aggregator(context: EngineerContext) -> MagicMock:
    aggregator = MagicMock()
    aggregator.build.return_value = context
    return aggregator


@pytest.fixture
def engineer_ai() -> MagicMock:
    return MagicMock(spec=EngineerAiService)


@pytest.fixture
def engineer_voice() -> MagicMock:
    return MagicMock(spec=EngineerVoiceService)


@pytest.fixture
def loop() -> asyncio.AbstractEventLoop:
    event_loop = asyncio.new_event_loop()
    yield event_loop
    event_loop.close()


@pytest.fixture
def orchestrator(
    ws_manager: MagicMock,
    context_aggregator: MagicMock,
    engineer_ai: MagicMock,
    engineer_voice: MagicMock,
    loop: asyncio.AbstractEventLoop,
) -> VoiceConversationOrchestrator:
    return VoiceConversationOrchestrator(
        ws_manager,
        context_aggregator,
        engineer_ai,
        engineer_voice,
        loop=loop,
    )


def _run_broadcasts(loop: asyncio.AbstractEventLoop, ws_manager: MagicMock) -> None:
    loop.run_until_complete(asyncio.sleep(0))
    assert ws_manager.broadcast.await_count >= 1


def test_handle_transcript_happy_path(
    orchestrator: VoiceConversationOrchestrator,
    engineer_ai: MagicMock,
    engineer_voice: MagicMock,
    ws_manager: MagicMock,
    loop: asyncio.AbstractEventLoop,
) -> None:
    engineer_ai.ask.return_value = EngineerAskResult(
        text="P3, fuel looks good.",
        model="gpt-4o-mini",
        latency_ms=120,
    )
    engineer_voice.speak.return_value = VoicePipelineResult.ok(
        SynthesisResult(text="P3, fuel looks good.")
    )

    orchestrator.handle_transcript(text="where am I?", intent="position")
    _run_broadcasts(loop, ws_manager)

    engineer_ai.ask.assert_called_once()
    ask_kwargs = engineer_ai.ask.call_args.kwargs
    assert ask_kwargs.get("personality") is None
    engineer_voice.speak.assert_called_once_with("P3, fuel looks good.")

    messages = [call.args[0] for call in ws_manager.broadcast.await_args_list]
    assert messages[0]["data"]["role"] == "driver"
    assert messages[0]["data"]["text"] == "where am I?"
    assert messages[0]["data"]["intent"] == "position"
    assert messages[0]["data"]["track_name"] == "Spa"
    assert messages[0]["data"]["session_type"] == "Race"
    assert messages[1]["data"]["role"] == "engineer"
    assert messages[1]["data"]["text"] == "P3, fuel looks good."


def test_handle_transcript_missing_ai_config(
    ws_manager: MagicMock,
    context_aggregator: MagicMock,
    engineer_voice: MagicMock,
    loop: asyncio.AbstractEventLoop,
) -> None:
    orchestrator = VoiceConversationOrchestrator(
        ws_manager,
        context_aggregator,
        None,
        engineer_voice,
        loop=loop,
    )

    orchestrator.handle_transcript(text="where am I?", intent="position")
    _run_broadcasts(loop, ws_manager)

    engineer_voice.speak.assert_not_called()
    messages = [call.args[0] for call in ws_manager.broadcast.await_args_list]
    assert messages[0]["data"]["role"] == "driver"
    assert messages[1]["data"]["role"] == "engineer"
    assert messages[1]["data"]["text"] == AI_NOT_CONFIGURED_MESSAGE


def test_handle_transcript_missing_tts_config(
    ws_manager: MagicMock,
    context_aggregator: MagicMock,
    engineer_ai: MagicMock,
    loop: asyncio.AbstractEventLoop,
) -> None:
    orchestrator = VoiceConversationOrchestrator(
        ws_manager,
        context_aggregator,
        engineer_ai,
        None,
        loop=loop,
    )

    orchestrator.handle_transcript(text="where am I?", intent="position")
    _run_broadcasts(loop, ws_manager)

    engineer_ai.ask.assert_not_called()
    messages = [call.args[0] for call in ws_manager.broadcast.await_args_list]
    assert messages[0]["data"]["role"] == "driver"
    assert messages[1]["data"]["role"] == "engineer"
    assert messages[1]["data"]["text"] == TTS_NOT_CONFIGURED_MESSAGE


def test_handle_transcript_llm_fallback_still_speaks(
    orchestrator: VoiceConversationOrchestrator,
    engineer_ai: MagicMock,
    engineer_voice: MagicMock,
    ws_manager: MagicMock,
    loop: asyncio.AbstractEventLoop,
) -> None:
    engineer_ai.ask.return_value = EngineerAskResult(
        text=LLM_FALLBACK_MESSAGE,
        fallback_used=True,
    )
    engineer_voice.speak.return_value = VoicePipelineResult.ok(
        SynthesisResult(text=LLM_FALLBACK_MESSAGE)
    )

    orchestrator.handle_transcript(text="where am I?", intent="position")
    _run_broadcasts(loop, ws_manager)

    engineer_voice.speak.assert_called_once_with(LLM_FALLBACK_MESSAGE)
    messages = [call.args[0] for call in ws_manager.broadcast.await_args_list]
    assert messages[1]["data"]["text"] == LLM_FALLBACK_MESSAGE


def test_handle_transcript_uses_personality_settings(
    ws_manager: MagicMock,
    context_aggregator: MagicMock,
    engineer_ai: MagicMock,
    engineer_voice: MagicMock,
    loop: asyncio.AbstractEventLoop,
) -> None:
    personality_settings = PersonalitySettings(PersonalityMode.CALM)
    orchestrator = VoiceConversationOrchestrator(
        ws_manager,
        context_aggregator,
        engineer_ai,
        engineer_voice,
        personality_settings=personality_settings,
        loop=loop,
    )
    engineer_ai.ask.return_value = EngineerAskResult(text="P3.")
    engineer_voice.speak.return_value = VoicePipelineResult.ok(
        SynthesisResult(text="P3.")
    )

    orchestrator.handle_transcript(text="where am I?", intent="position")
    _run_broadcasts(loop, ws_manager)

    assert engineer_ai.ask.call_args.kwargs["personality"] == PersonalityMode.CALM


def test_handle_transcript_tts_failure_still_broadcasts_engineer_reply(
    orchestrator: VoiceConversationOrchestrator,
    engineer_ai: MagicMock,
    engineer_voice: MagicMock,
    ws_manager: MagicMock,
    loop: asyncio.AbstractEventLoop,
) -> None:
    engineer_ai.ask.return_value = EngineerAskResult(text="Stay out.")
    engineer_voice.speak.return_value = VoicePipelineResult.fail(
        error_code=VoiceErrorCode.NETWORK,
        message="connection reset",
    )

    orchestrator.handle_transcript(text="should I pit?", intent="fuel")
    _run_broadcasts(loop, ws_manager)

    messages = [call.args[0] for call in ws_manager.broadcast.await_args_list]
    assert messages[1]["data"]["text"] == "Stay out."
