from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from race_engineer.ai.prompt.models import PersonalityMode
from race_engineer.settings.personality import PersonalitySettings
from race_engineer.settings.volume import VoiceVolumeSettings
from race_engineer.voice.audio.volume import MAX_VOICE_OUTPUT_VOLUME

router = APIRouter(tags=["settings"])


class PersonalitySettingsBody(BaseModel):
    mode: PersonalityMode = Field(..., description="Engineer tone: calm, direct, or intense")


class PersonalitySettingsResponse(BaseModel):
    mode: PersonalityMode


def get_personality_settings(request: Request) -> PersonalitySettings:
    settings = getattr(request.app.state, "personality_settings", None)
    if settings is None:
        return PersonalitySettings()
    return settings


PersonalitySettingsDep = Annotated[PersonalitySettings, Depends(get_personality_settings)]


@router.get("/settings/personality")
def get_personality(settings: PersonalitySettingsDep) -> PersonalitySettingsResponse:
    return PersonalitySettingsResponse(mode=settings.mode)


@router.put("/settings/personality")
def update_personality(
    body: PersonalitySettingsBody,
    settings: PersonalitySettingsDep,
) -> PersonalitySettingsResponse:
    settings.set_mode(body.mode)
    return PersonalitySettingsResponse(mode=settings.mode)


class VoiceVolumeBody(BaseModel):
    volume: float = Field(
        ...,
        ge=0.0,
        le=MAX_VOICE_OUTPUT_VOLUME,
        description="Engineer TTS playback gain (0.0–2.0; values above 1.0 boost over engine noise)",
    )


class VoiceVolumeResponse(BaseModel):
    volume: float


def get_voice_volume_settings(request: Request) -> VoiceVolumeSettings:
    settings = getattr(request.app.state, "voice_volume_settings", None)
    if settings is None:
        return VoiceVolumeSettings()
    return settings


VoiceVolumeSettingsDep = Annotated[VoiceVolumeSettings, Depends(get_voice_volume_settings)]


@router.get("/settings/volume")
def get_voice_volume(settings: VoiceVolumeSettingsDep) -> VoiceVolumeResponse:
    return VoiceVolumeResponse(volume=settings.volume)


@router.put("/settings/volume")
def update_voice_volume(
    body: VoiceVolumeBody,
    settings: VoiceVolumeSettingsDep,
) -> VoiceVolumeResponse:
    settings.set_volume(body.volume)
    return VoiceVolumeResponse(volume=settings.volume)
