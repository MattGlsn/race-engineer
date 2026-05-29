from __future__ import annotations

import logging
from typing import Any

import httpx

from race_engineer.voice.stt.config import ElevenLabsSttConfig
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.stt.result import VoicePipelineResult

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 10.0


class ElevenLabsSttClient:
    """Send audio to ElevenLabs Scribe speech-to-text."""

    def __init__(
        self,
        config: ElevenLabsSttConfig,
        *,
        http_client: httpx.Client | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._config = config
        self._timeout_seconds = timeout_seconds
        self._http_client = http_client
        self._owns_client = http_client is None

    def transcribe(
        self,
        wav_bytes: bytes,
        *,
        language: str = "en",
    ) -> VoicePipelineResult[TranscriptResult]:
        if not wav_bytes:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.EMPTY_AUDIO,
                message="wav payload is empty",
            )

        client = self._http_client or httpx.Client(timeout=self._timeout_seconds)
        try:
            response = client.post(
                f"{self._config.base_url}/v1/speech-to-text",
                headers={"xi-api-key": self._config.api_key},
                data={
                    "model_id": self._config.model_id,
                    "language_code": language,
                },
                files={"file": ("audio.wav", wav_bytes, "audio/wav")},
            )
        except httpx.TimeoutException:
            logger.exception("ElevenLabs STT request timed out")
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.NETWORK,
                message="ElevenLabs STT request timed out",
            )
        except httpx.HTTPError as exc:
            logger.exception("ElevenLabs STT network error")
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.NETWORK,
                message=str(exc),
            )
        finally:
            if self._owns_client:
                client.close()

        return self._parse_response(response)

    def close(self) -> None:
        if self._owns_client and self._http_client is not None:
            self._http_client.close()

    def _parse_response(
        self,
        response: httpx.Response,
    ) -> VoicePipelineResult[TranscriptResult]:
        if response.status_code == 401:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.INVALID_API_KEY,
                message="ElevenLabs rejected the API key",
            )
        if response.status_code == 429:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.RATE_LIMIT,
                message="ElevenLabs STT rate limit exceeded",
            )
        if response.status_code >= 500:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PROVIDER_ERROR,
                message=f"ElevenLabs STT server error ({response.status_code})",
            )
        if response.status_code >= 400:
            detail = _response_detail(response)
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PROVIDER_ERROR,
                message=detail or f"ElevenLabs STT request failed ({response.status_code})",
            )

        try:
            payload = response.json()
        except ValueError:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PROVIDER_ERROR,
                message="ElevenLabs STT returned invalid JSON",
            )

        text = payload.get("text")
        if not isinstance(text, str):
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PROVIDER_ERROR,
                message="ElevenLabs STT response missing transcript text",
            )

        language_code = payload.get("language_code")
        if language_code is not None and not isinstance(language_code, str):
            language_code = None

        duration_ms = _duration_ms_from_payload(payload)

        return VoicePipelineResult.ok(
            TranscriptResult(
                text=text,
                language_code=language_code,
                duration_ms=duration_ms,
            )
        )


def _duration_ms_from_payload(payload: dict[str, Any]) -> int | None:
    audio_duration_secs = payload.get("audio_duration_secs")
    if isinstance(audio_duration_secs, (int, float)) and audio_duration_secs >= 0:
        return int(audio_duration_secs * 1000)
    return None


def _response_detail(response: httpx.Response) -> str | None:
    try:
        payload: Any = response.json()
    except ValueError:
        return None

    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
    return None
