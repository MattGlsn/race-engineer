from __future__ import annotations

import logging
import os
import threading
from collections import deque

from race_engineer.proactive.suppression.workload import WorkloadMonitor
from race_engineer.settings.volume import VoiceVolumeSettings
from race_engineer.voice.audio.player import AudioPlayer, PlaybackError
from race_engineer.voice.audio.volume import load_voice_volume_config
from race_engineer.voice.speak_guard import SpeakGuard
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.tts.client import ElevenLabsTtsClient
from race_engineer.voice.tts.models import SynthesisResult

logger = logging.getLogger(__name__)

DEFAULT_MAX_PENDING_SPEECH = 4


class EngineerVoiceService:
    """Synthesize engineer speech and play it through local audio output."""

    def __init__(
        self,
        tts_client: ElevenLabsTtsClient,
        *,
        player: AudioPlayer | None = None,
        volume_settings: VoiceVolumeSettings | None = None,
        speak_guard: SpeakGuard | None = None,
        workload_monitor: WorkloadMonitor | None = None,
        max_pending_speech: int = DEFAULT_MAX_PENDING_SPEECH,
    ) -> None:
        self._tts_client = tts_client
        self._player = player or AudioPlayer()
        self._volume_settings = volume_settings or VoiceVolumeSettings(
            load_voice_volume_config().volume
        )
        self._speak_guard = speak_guard or SpeakGuard()
        self._workload_monitor = workload_monitor
        self._max_pending_speech = max_pending_speech
        self._pending_speech: deque[str] = deque()
        self._speak_lock = threading.Lock()

    def speak(self, text: str) -> VoicePipelineResult[SynthesisResult]:
        stripped = text.strip()
        if not stripped:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.EMPTY_AUDIO,
                message="text is empty",
            )

        with self._speak_lock:
            if (
                self._workload_monitor is not None
                and self._workload_monitor.should_suppress()
            ):
                self._pending_speech.append(stripped)
                while len(self._pending_speech) > self._max_pending_speech:
                    self._pending_speech.popleft()
                logger.info(
                    "deferring engineer speech during high workload (pid=%s)",
                    os.getpid(),
                )
                return VoicePipelineResult.ok(SynthesisResult(text=stripped))

            return self._play_locked(stripped)

    def flush_pending_speech(self) -> None:
        with self._speak_lock:
            if (
                self._workload_monitor is not None
                and self._workload_monitor.should_suppress()
            ):
                return
            while self._pending_speech:
                text = self._pending_speech.popleft()
                self._play_locked(text)

    def _play_locked(self, stripped: str) -> VoicePipelineResult[SynthesisResult]:
        if not self._speak_guard.claim(stripped):
            return VoicePipelineResult.ok(SynthesisResult(text=stripped))

        logger.info("engineer voice playback starting (pid=%s)", os.getpid())
        stream_result = self._tts_client.synthesize_stream(stripped)
        if not stream_result.success or stream_result.data is None:
            return VoicePipelineResult.fail(
                error_code=stream_result.error_code or VoiceErrorCode.PROVIDER_ERROR,
                message=stream_result.message or "synthesis failed",
            )

        try:
            self._player.play_stream(
                stream_result.data,
                volume=self._volume_settings.volume,
            )
        except PlaybackError as exc:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PROVIDER_ERROR,
                message=str(exc),
            )
        except OSError as exc:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PERMISSION_DENIED,
                message=str(exc),
            )

        return VoicePipelineResult.ok(SynthesisResult(text=stripped))
