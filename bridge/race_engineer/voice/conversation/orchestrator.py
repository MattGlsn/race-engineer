from __future__ import annotations

import asyncio
import logging

from race_engineer.ai.service import EngineerAiService
from race_engineer.settings.personality import PersonalitySettings
from race_engineer.api.ws.manager import WebSocketConnectionManager
from race_engineer.api.ws.messages import build_transcript_message
from race_engineer.context.aggregator import ContextAggregator
from race_engineer.voice.engineer import EngineerVoiceService

logger = logging.getLogger(__name__)

AI_NOT_CONFIGURED_MESSAGE = (
    "Race engineer AI is not configured. Set OPENAI_API_KEY."
)
TTS_NOT_CONFIGURED_MESSAGE = (
    "Engineer voice is not configured. Set ELEVENLABS_VOICE_ID."
)


class VoiceConversationOrchestrator:
    """Run the push-to-talk conversation loop after STT completes."""

    def __init__(
        self,
        ws_manager: WebSocketConnectionManager,
        context_aggregator: ContextAggregator,
        engineer_ai: EngineerAiService | None,
        engineer_voice: EngineerVoiceService | None,
        *,
        personality_settings: PersonalitySettings | None = None,
        loop: asyncio.AbstractEventLoop | None = None,
    ) -> None:
        self._ws_manager = ws_manager
        self._context_aggregator = context_aggregator
        self._engineer_ai = engineer_ai
        self._engineer_voice = engineer_voice
        self._personality_settings = personality_settings
        self._loop = loop

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def handle_transcript(self, *, text: str, intent: str | None) -> None:
        context = self._context_aggregator.build()
        track_name = context.session.track_name
        session_type = context.session.session_type

        self._broadcast_transcript(
            role="driver",
            text=text,
            intent=intent,
            track_name=track_name,
            session_type=session_type,
        )

        config_error = self._config_error_message()
        if config_error is not None:
            self._broadcast_transcript(
                role="engineer",
                text=config_error,
                track_name=track_name,
                session_type=session_type,
            )
            return

        assert self._engineer_ai is not None
        assert self._engineer_voice is not None

        personality = (
            self._personality_settings.mode
            if self._personality_settings is not None
            else None
        )
        result = self._engineer_ai.ask(
            text,
            context,
            intent=intent,
            personality=personality,
        )
        self._broadcast_transcript(
            role="engineer",
            text=result.text,
            track_name=track_name,
            session_type=session_type,
        )

        speak_result = self._engineer_voice.speak(result.text)
        if not speak_result.success:
            logger.warning(
                "engineer voice playback failed: %s",
                speak_result.message or "unknown error",
            )

    def _config_error_message(self) -> str | None:
        if self._engineer_ai is None:
            return AI_NOT_CONFIGURED_MESSAGE
        if self._engineer_voice is None:
            return TTS_NOT_CONFIGURED_MESSAGE
        return None

    def _broadcast_transcript(
        self,
        *,
        role: str,
        text: str,
        intent: str | None = None,
        track_name: str | None = None,
        session_type: str | None = None,
    ) -> None:
        if self._loop is None:
            logger.warning("voice conversation transcript dropped: event loop not bound")
            return

        message = build_transcript_message(
            role=role,
            text=text,
            intent=intent,
            track_name=track_name,
            session_type=session_type,
        )
        asyncio.run_coroutine_threadsafe(
            self._ws_manager.broadcast(message),
            self._loop,
        )
