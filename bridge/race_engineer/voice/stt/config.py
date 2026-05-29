import os
from dataclasses import dataclass

DEFAULT_ELEVENLABS_STT_MODEL = "scribe_v2"
DEFAULT_ELEVENLABS_BASE_URL = "https://api.elevenlabs.io"


@dataclass(frozen=True, slots=True)
class ElevenLabsSttConfig:
    api_key: str
    model_id: str = DEFAULT_ELEVENLABS_STT_MODEL
    base_url: str = DEFAULT_ELEVENLABS_BASE_URL


def load_elevenlabs_stt_config() -> ElevenLabsSttConfig | None:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        return None

    model_id = os.environ.get("ELEVENLABS_STT_MODEL", DEFAULT_ELEVENLABS_STT_MODEL)
    base_url = os.environ.get("ELEVENLABS_BASE_URL", DEFAULT_ELEVENLABS_BASE_URL)
    return ElevenLabsSttConfig(
        api_key=api_key,
        model_id=model_id,
        base_url=base_url.rstrip("/"),
    )
