from race_engineer.voice.audio.models import AudioBuffer
from race_engineer.voice.audio.recorder import AudioRecorder, RecordingError
from race_engineer.voice.audio.wav import audio_buffer_to_wav
from race_engineer.voice.stt.client import ElevenLabsSttClient
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.stt.validation import validate_audio


class VoicePipeline:
    """Record audio, send to STT, and return structured transcripts."""

    def __init__(
        self,
        stt_client: ElevenLabsSttClient,
        *,
        recorder: AudioRecorder | None = None,
    ) -> None:
        self._stt_client = stt_client
        self._recorder = recorder or AudioRecorder()

    def transcribe_buffer(
        self,
        buffer: AudioBuffer,
        *,
        language: str = "en",
    ) -> VoicePipelineResult[TranscriptResult]:
        errors = validate_audio(buffer)
        if errors:
            return _validation_failure(errors[0])

        wav_bytes = audio_buffer_to_wav(buffer)
        result = self._stt_client.transcribe(wav_bytes, language=language)
        if not result.success or result.data is None:
            return result

        return VoicePipelineResult.ok(
            TranscriptResult(
                text=result.data.text,
                language_code=result.data.language_code,
                duration_ms=int(buffer.duration_seconds * 1000),
            )
        )

    def transcribe_wav(
        self,
        wav_bytes: bytes,
        *,
        language: str = "en",
    ) -> VoicePipelineResult[TranscriptResult]:
        return self._stt_client.transcribe(wav_bytes, language=language)

    def transcribe_from_microphone(
        self,
        *,
        language: str = "en",
    ) -> VoicePipelineResult[TranscriptResult]:
        try:
            self._recorder.start()
            buffer = self._recorder.stop()
        except RecordingError as exc:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PROVIDER_ERROR,
                message=str(exc),
            )
        except OSError as exc:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PERMISSION_DENIED,
                message=str(exc),
            )

        return self.transcribe_buffer(buffer, language=language)


def _validation_failure(message: str) -> VoicePipelineResult[TranscriptResult]:
    if message == "audio buffer is empty":
        error_code = VoiceErrorCode.EMPTY_AUDIO
    else:
        error_code = VoiceErrorCode.AUDIO_TOO_SHORT

    return VoicePipelineResult.fail(error_code=error_code, message=message)
