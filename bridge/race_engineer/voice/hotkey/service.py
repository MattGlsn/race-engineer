from __future__ import annotations

import asyncio
import logging
from typing import Any

from race_engineer.api.ws.manager import WebSocketConnectionManager
from race_engineer.api.ws.messages import build_transcript_message
from race_engineer.voice.hotkey.config import VoiceHotkeyConfig, load_voice_hotkey_config
from race_engineer.voice.hotkey.controller import VoiceHotkeyController
from race_engineer.voice.hotkey.errors import HotkeyRegistrationError
from race_engineer.voice.hotkey.listener import GlobalHotkeyListener
from race_engineer.voice.intent.router import IntentRouter
from race_engineer.voice.pipeline import VoicePipeline
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult

logger = logging.getLogger(__name__)


class VoiceHotkeyService:
    """Runs a global push-to-talk hotkey and broadcasts transcripts."""

    def __init__(
        self,
        pipeline: VoicePipeline,
        ws_manager: WebSocketConnectionManager,
        *,
        config: VoiceHotkeyConfig | None = None,
        listener: GlobalHotkeyListener | None = None,
        intent_router: IntentRouter | None = None,
    ) -> None:
        self._pipeline = pipeline
        self._ws_manager = ws_manager
        self._config = config or load_voice_hotkey_config()
        self._listener = listener
        self._intent_router = intent_router or IntentRouter()
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        if self._listener is not None:
            return
        controller = VoiceHotkeyController(
            self._pipeline,
            on_transcript=self._on_transcript,
        )
        self._listener = GlobalHotkeyListener(self._config.binding, controller)
        try:
            self._listener.start()
        except HotkeyRegistrationError:
            self._listener = None
            raise

    def stop(self) -> None:
        if self._listener is None:
            return

        self._listener.stop()
        self._listener = None
        self._loop = None

    def _on_transcript(self, result: VoicePipelineResult[TranscriptResult]) -> None:
        if not result.success or result.data is None:
            logger.warning(
                "voice hotkey transcription failed: %s",
                result.message or "unknown error",
            )
            return

        if self._loop is None:
            logger.warning("voice hotkey transcript dropped: event loop not bound")
            return

        routed = self._intent_router.route(result.data.text)
        message = build_transcript_message(
            role="driver",
            text=result.data.text,
            intent=routed.intent.value,
        )
        asyncio.run_coroutine_threadsafe(
            self._ws_manager.broadcast(message),
            self._loop,
        )
