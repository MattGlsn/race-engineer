from __future__ import annotations

import asyncio
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from race_engineer.api.ws.manager import WebSocketConnectionManager
from race_engineer.api.ws.messages import build_voice_state_message
from race_engineer.settings.hotkey import VoiceHotkeySettings
from race_engineer.voice.conversation.orchestrator import VoiceConversationOrchestrator
from race_engineer.voice.hotkey.controller import VoiceHotkeyController
from race_engineer.voice.hotkey.errors import HotkeyRegistrationError
from race_engineer.voice.hotkey.config import load_joystick_ptt_config
from race_engineer.voice.hotkey.joystick_listener import JoystickPttListener
from race_engineer.voice.hotkey.listener import GlobalHotkeyListener
from race_engineer.voice.hotkey.process_lock import (
    DEFAULT_LOCK_RETRY_ATTEMPTS,
    DEFAULT_LOCK_RETRY_DELAY_SECONDS,
    VoiceHotkeyProcessLock,
)
from race_engineer.voice.intent.router import IntentRouter
from race_engineer.voice.pipeline import VoicePipeline
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult

logger = logging.getLogger(__name__)


class VoiceHotkeyService:
    """Runs a global push-to-talk hotkey and drives the conversation pipeline."""

    def __init__(
        self,
        pipeline: VoicePipeline,
        *,
        ws_manager: WebSocketConnectionManager | None = None,
        hotkey_settings: VoiceHotkeySettings | None = None,
        listener: GlobalHotkeyListener | None = None,
        intent_router: IntentRouter | None = None,
        orchestrator: VoiceConversationOrchestrator | None = None,
        executor: ThreadPoolExecutor | None = None,
        process_lock: VoiceHotkeyProcessLock | None = None,
    ) -> None:
        self._pipeline = pipeline
        self._ws_manager = ws_manager
        self._hotkey_settings = hotkey_settings or VoiceHotkeySettings()
        self._listener = listener
        self._joystick_listener: JoystickPttListener | None = None
        self._joystick_binding = load_joystick_ptt_config()
        self._controller: VoiceHotkeyController | None = None
        self._intent_router = intent_router or IntentRouter()
        self._orchestrator = orchestrator
        self._executor = executor or ThreadPoolExecutor(
            max_workers=1,
            thread_name_prefix="voice-conversation",
        )
        self._owns_executor = executor is None
        self._process_lock = process_lock or VoiceHotkeyProcessLock()
        self._conversation_lock = threading.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop
        if self._orchestrator is not None:
            self._orchestrator.bind_loop(loop)
        if self._listener is not None:
            return
        self._start_listener()

    def stop(self) -> None:
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        if self._joystick_listener is not None:
            self._joystick_listener.stop()
            self._joystick_listener = None
        self._controller = None
        self._loop = None
        self._process_lock.release()
        if self._owns_executor:
            self._executor.shutdown(wait=False)

    def rebind(self) -> None:
        """Apply the current hotkey settings binding to the global listener."""
        if self._loop is None:
            return

        if self._controller is not None and self._controller.is_ptt_active:
            self._controller.on_release()

        if self._listener is not None:
            self._listener.stop()
            self._listener = None

        self._start_listener()

    def _start_listener(self) -> None:
        if self._controller is None:
            self._controller = VoiceHotkeyController(
                self._pipeline,
                on_transcript=self._on_transcript,
                on_state_change=self._broadcast_voice_state,
            )

        if self._listener is not None:
            return

        if not self._process_lock.acquire(
            retry_attempts=DEFAULT_LOCK_RETRY_ATTEMPTS,
            retry_delay_seconds=DEFAULT_LOCK_RETRY_DELAY_SECONDS,
        ):
            logger.warning(
                "voice hotkey listener not started: another bridge process owns PTT"
            )
            return

        self._listener = GlobalHotkeyListener(
            self._hotkey_settings.binding,
            self._controller,
        )
        try:
            self._listener.start()
            self._start_joystick_listener()
        except HotkeyRegistrationError:
            self._listener = None
            self._process_lock.release()
            raise

    def _start_joystick_listener(self) -> None:
        if self._joystick_binding is None or self._controller is None:
            return
        if self._joystick_listener is not None:
            return

        self._joystick_listener = JoystickPttListener(
            self._joystick_binding,
            self._controller,
        )
        try:
            self._joystick_listener.start()
        except HotkeyRegistrationError as exc:
            self._joystick_listener = None
            logger.warning(
                "joystick push-to-talk not started for binding %s: %s",
                self._joystick_binding.format(),
                exc,
            )

    def _broadcast_voice_state(self, status: str) -> None:
        if self._ws_manager is None or self._loop is None:
            return

        message = build_voice_state_message(status=status)
        asyncio.run_coroutine_threadsafe(
            self._ws_manager.broadcast(message),
            self._loop,
        )

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

        if self._orchestrator is None:
            logger.warning("voice hotkey transcript dropped: orchestrator not configured")
            return

        routed = self._intent_router.route(result.data.text)
        if not self._conversation_lock.acquire(blocking=False):
            logger.warning(
                "voice hotkey transcript ignored: conversation already in progress"
            )
            return

        self._executor.submit(
            self._run_conversation,
            text=result.data.text,
            intent=routed.intent.value,
        )

    def _run_conversation(self, *, text: str, intent: str) -> None:
        if self._orchestrator is None:
            self._conversation_lock.release()
            return
        try:
            self._orchestrator.handle_transcript(text=text, intent=intent)
        except Exception:
            logger.exception("voice hotkey conversation failed for transcript %r", text)
        finally:
            self._conversation_lock.release()
