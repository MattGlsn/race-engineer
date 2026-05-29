from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import AbstractContextManager
from typing import Any

import httpx

from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.tts.config import ElevenLabsTtsConfig

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 15.0
DEFAULT_STREAM_CHUNK_SIZE = 4096


class ElevenLabsTtsClient:
    """Stream PCM audio from ElevenLabs text-to-speech."""

    def __init__(
        self,
        config: ElevenLabsTtsConfig,
        *,
        http_client: httpx.Client | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        stream_chunk_size: int = DEFAULT_STREAM_CHUNK_SIZE,
    ) -> None:
        self._config = config
        self._timeout_seconds = timeout_seconds
        self._stream_chunk_size = stream_chunk_size
        self._http_client = http_client
        self._owns_client = http_client is None

    def synthesize_stream(
        self,
        text: str,
    ) -> VoicePipelineResult[Iterator[bytes]]:
        stripped = text.strip()
        if not stripped:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.EMPTY_AUDIO,
                message="text is empty",
            )

        client = self._http_client or httpx.Client(timeout=self._timeout_seconds)
        owns_client = self._owns_client and self._http_client is None
        url = (
            f"{self._config.base_url}/v1/text-to-speech/"
            f"{self._config.voice_id}/stream"
        )
        stream_cm = client.stream(
            "POST",
            url,
            headers={
                "xi-api-key": self._config.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/pcm",
            },
            params={"output_format": self._config.output_format},
            json={
                "text": stripped,
                "model_id": self._config.model_id,
            },
        )
        try:
            response = stream_cm.__enter__()
        except httpx.TimeoutException:
            logger.exception("ElevenLabs TTS request timed out")
            if owns_client:
                client.close()
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.NETWORK,
                message="ElevenLabs TTS request timed out",
            )
        except httpx.HTTPError as exc:
            logger.exception("ElevenLabs TTS network error")
            if owns_client:
                client.close()
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.NETWORK,
                message=str(exc),
            )

        error = self._stream_error_result(response)
        if error is not None:
            stream_cm.__exit__(None, None, None)
            if owns_client:
                client.close()
            return error

        return VoicePipelineResult.ok(
            _StreamingPcmChunks(
                stream_cm=stream_cm,
                response=response,
                chunk_size=self._stream_chunk_size,
                client=client if owns_client else None,
            )
        )

    def close(self) -> None:
        if self._owns_client and self._http_client is not None:
            self._http_client.close()

    def _stream_error_result(
        self,
        response: httpx.Response,
    ) -> VoicePipelineResult[Iterator[bytes]] | None:
        if response.status_code == 401:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.INVALID_API_KEY,
                message="ElevenLabs rejected the API key",
            )
        if response.status_code == 429:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.RATE_LIMIT,
                message="ElevenLabs TTS rate limit exceeded",
            )
        if response.status_code >= 500:
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PROVIDER_ERROR,
                message=f"ElevenLabs TTS server error ({response.status_code})",
            )
        if response.status_code >= 400:
            detail = _response_detail(response)
            return VoicePipelineResult.fail(
                error_code=VoiceErrorCode.PROVIDER_ERROR,
                message=detail or f"ElevenLabs TTS request failed ({response.status_code})",
            )
        return None


class _StreamingPcmChunks(Iterator[bytes]):
    def __init__(
        self,
        *,
        stream_cm: AbstractContextManager[httpx.Response],
        response: httpx.Response,
        chunk_size: int,
        client: httpx.Client | None,
    ) -> None:
        self._stream_cm = stream_cm
        self._response = response
        self._chunk_size = chunk_size
        self._client = client
        self._iterator = response.iter_bytes(chunk_size=chunk_size)

    def __iter__(self) -> Iterator[bytes]:
        return self

    def __next__(self) -> bytes:
        try:
            chunk = next(self._iterator)
        except StopIteration:
            self._close()
            raise
        if not chunk:
            return self.__next__()
        return chunk

    def _close(self) -> None:
        self._stream_cm.__exit__(None, None, None)
        if self._client is not None:
            self._client.close()


def _response_detail(response: httpx.Response) -> str | None:
    try:
        payload: Any = response.json()
    except ValueError:
        text = response.text.strip()
        return text or None

    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
    return None
