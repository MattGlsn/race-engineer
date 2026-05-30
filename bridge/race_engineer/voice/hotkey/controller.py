from __future__ import annotations

import logging
import threading
from collections.abc import Callable

from race_engineer.voice.audio.recorder import RecordingError
from race_engineer.voice.pipeline import VoicePipeline
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult

logger = logging.getLogger(__name__)

TranscriptCallback = Callable[[VoicePipelineResult[TranscriptResult]], None]
StateChangeCallback = Callable[[str], None]


class VoiceHotkeyController:
    """Maps push-to-talk press/release events to microphone recording."""

    def __init__(
        self,
        pipeline: VoicePipeline,
        *,
        on_transcript: TranscriptCallback | None = None,
        on_state_change: StateChangeCallback | None = None,
    ) -> None:
        self._pipeline = pipeline
        self._on_transcript = on_transcript
        self._on_state_change = on_state_change
        self._lock = threading.Lock()
        self._ptt_active = False

    @property
    def is_ptt_active(self) -> bool:
        with self._lock:
            return self._ptt_active

    def on_press(self) -> None:
        with self._lock:
            if self._ptt_active or self._pipeline.recorder.is_recording:
                logger.debug("hotkey press ignored: recording already active")
                return

            try:
                self._pipeline.start_recording()
            except RecordingError as exc:
                logger.warning("hotkey press failed: %s", exc)
                return

            self._ptt_active = True

        if self._on_state_change is not None:
            self._on_state_change("recording")

    def on_release(self) -> None:
        with self._lock:
            if not self._ptt_active:
                logger.debug("hotkey release ignored: push-to-talk not active")
                return
            self._ptt_active = False

        if self._on_state_change is not None:
            self._on_state_change("idle")

        result = self._pipeline.stop_and_transcribe()
        if self._on_transcript is not None:
            self._on_transcript(result)
