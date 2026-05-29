from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from pydantic import BaseModel, Field

from race_engineer.voice.engineer import EngineerVoiceService
from race_engineer.voice.intent.router import route_intent
from race_engineer.voice.pipeline import VoicePipeline
from race_engineer.voice.stt.errors import VoiceErrorCode
from race_engineer.voice.stt.result import VoicePipelineResult
from race_engineer.voice.stt.models import TranscriptResult
from race_engineer.voice.tts.models import SynthesisResult

router = APIRouter(tags=["voice"])


class SpeakRequest(BaseModel):
    text: str = Field(..., min_length=1)


class RouteRequest(BaseModel):
    text: str = Field(..., min_length=1)


def get_voice_pipeline(request: Request) -> VoicePipeline:
    pipeline = getattr(request.app.state, "voice_pipeline", None)
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="voice transcription is not configured (set ELEVENLABS_API_KEY)",
        )
    return pipeline


VoicePipelineDep = Annotated[VoicePipeline, Depends(get_voice_pipeline)]


def get_engineer_voice(request: Request) -> EngineerVoiceService:
    service = getattr(request.app.state, "engineer_voice", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "engineer voice is not configured "
                "(set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID)"
            ),
        )
    return service


EngineerVoiceDep = Annotated[EngineerVoiceService, Depends(get_engineer_voice)]


@router.post("/voice/transcribe")
async def transcribe_voice(
    pipeline: VoicePipelineDep,
    file: UploadFile = File(...),
) -> dict[str, Any]:
    wav_bytes = await file.read()
    result = pipeline.transcribe_wav(wav_bytes)
    return _response_from_result(result)


@router.post("/voice/speak")
async def speak_voice(
    body: SpeakRequest,
    service: EngineerVoiceDep,
) -> dict[str, Any]:
    result = service.speak(body.text)
    return _speak_response_from_result(result)


@router.post("/voice/route")
async def route_voice(body: RouteRequest) -> dict[str, Any]:
    routed = route_intent(body.text)
    return {
        "success": True,
        "text": routed.text,
        "intent": routed.intent.value,
    }


def _response_from_result(
    result: VoicePipelineResult[TranscriptResult],
) -> dict[str, Any]:
    if result.success and result.data is not None:
        return {
            "success": True,
            "text": result.data.text,
            "language_code": result.data.language_code,
            "duration_ms": result.data.duration_ms,
        }

    error_code = result.error_code.value if result.error_code else "unknown"
    message = result.message or "transcription failed"
    status_code = _status_code_for_error(result.error_code)

    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error_code": error_code,
            "message": message,
        },
    )


def _speak_response_from_result(
    result: VoicePipelineResult[SynthesisResult],
) -> dict[str, Any]:
    if result.success and result.data is not None:
        return {
            "success": True,
            "text": result.data.text,
            "duration_ms": result.data.duration_ms,
        }

    error_code = result.error_code.value if result.error_code else "unknown"
    message = result.message or "speech synthesis failed"
    status_code = _status_code_for_error(result.error_code)

    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error_code": error_code,
            "message": message,
        },
    )


def _status_code_for_error(error_code: VoiceErrorCode | None) -> int:
    if error_code in {VoiceErrorCode.EMPTY_AUDIO, VoiceErrorCode.AUDIO_TOO_SHORT}:
        return status.HTTP_400_BAD_REQUEST
    if error_code == VoiceErrorCode.INVALID_API_KEY:
        return status.HTTP_503_SERVICE_UNAVAILABLE
    if error_code == VoiceErrorCode.RATE_LIMIT:
        return status.HTTP_429_TOO_MANY_REQUESTS
    if error_code == VoiceErrorCode.NETWORK:
        return status.HTTP_502_BAD_GATEWAY
    return status.HTTP_502_BAD_GATEWAY
