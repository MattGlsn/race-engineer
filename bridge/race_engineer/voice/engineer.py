from race_engineer.voice.audio.player import AudioPlayer, PlaybackError
from race_engineer.voice.audio.volume import VoiceVolumeConfig, load_voice_volume_config
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.tts.client import ElevenLabsTtsClient
from race_engineer.voice.tts.models import SynthesisResult


class EngineerVoiceService:
    """Synthesize engineer speech and play it through local audio output."""

    def __init__(
        self,
        tts_client: ElevenLabsTtsClient,
        *,
        player: AudioPlayer | None = None,
        volume_config: VoiceVolumeConfig | None = None,
    ) -> None:
        self._tts_client = tts_client
        self._player = player or AudioPlayer()
        self._volume_config = volume_config or load_voice_volume_config()

    def speak(self, text: str) -> VoicePipelineResult[SynthesisResult]:
        stream_result = self._tts_client.synthesize_stream(text)
        if not stream_result.success or stream_result.data is None:
            return VoicePipelineResult.fail(
                error_code=stream_result.error_code or VoiceErrorCode.PROVIDER_ERROR,
                message=stream_result.message or "synthesis failed",
            )

        stripped = text.strip()
        try:
            self._player.play_stream(
                stream_result.data,
                volume=self._volume_config.volume,
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
