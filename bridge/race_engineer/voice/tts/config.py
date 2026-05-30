import os
from dataclasses import dataclass

DEFAULT_ELEVENLABS_TTS_MODEL = "eleven_turbo_v2_5"
DEFAULT_ELEVENLABS_TTS_OUTPUT_FORMAT = "pcm_16000"
DEFAULT_ELEVENLABS_TTS_SPEED = 0.9
DEFAULT_ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"


@dataclass(frozen=True, slots=True)
class ElevenLabsTtsConfig:
    api_key: str
    voice_id: str
    model_id: str = DEFAULT_ELEVENLABS_TTS_MODEL
    output_format: str = DEFAULT_ELEVENLABS_TTS_OUTPUT_FORMAT
    speed: float = DEFAULT_ELEVENLABS_TTS_SPEED
    base_url: str = DEFAULT_ELEVENLABS_BASE_URL


def load_elevenlabs_tts_config() -> ElevenLabsTtsConfig | None:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
    if not api_key or not voice_id:
        return None

    model_id = os.environ.get("ELEVENLABS_TTS_MODEL", DEFAULT_ELEVENLABS_TTS_MODEL)
    output_format = os.environ.get(
        "ELEVENLABS_TTS_OUTPUT_FORMAT",
        DEFAULT_ELEVENLABS_TTS_OUTPUT_FORMAT,
    )
    speed_raw = os.environ.get("ELEVENLABS_TTS_SPEED")
    if speed_raw is None:
        speed = DEFAULT_ELEVENLABS_TTS_SPEED
    else:
        try:
            speed = float(speed_raw)
        except ValueError as exc:
            raise ValueError("ELEVENLABS_TTS_SPEED must be a number") from exc
    base_url = os.environ.get("ELEVENLABS_BASE_URL", DEFAULT_ELEVENLABS_BASE_URL)
    return ElevenLabsTtsConfig(
        api_key=api_key,
        voice_id=voice_id,
        model_id=model_id,
        output_format=output_format,
        speed=speed,
        base_url=base_url.rstrip("/"),
    )
