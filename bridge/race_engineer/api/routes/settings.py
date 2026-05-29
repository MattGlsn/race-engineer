from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from race_engineer.ai.prompt.models import PersonalityMode
from race_engineer.settings.hotkey import VoiceHotkeySettings
from race_engineer.settings.personality import PersonalitySettings
from race_engineer.settings.volume import VoiceVolumeSettings
from race_engineer.voice.audio.volume import MAX_VOICE_OUTPUT_VOLUME
from race_engineer.voice.hotkey.binding import HotkeyBinding
from race_engineer.voice.hotkey.errors import HotkeyRegistrationError
from race_engineer.voice.hotkey.service import VoiceHotkeyService

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


class VoiceHotkeyBody(BaseModel):
    hotkey: str = Field(
        ...,
        min_length=1,
        description='Push-to-talk binding, e.g. "ctrl+shift+space"',
    )


class VoiceHotkeyResponse(BaseModel):
    hotkey: str


def get_voice_hotkey_settings(request: Request) -> VoiceHotkeySettings:
    settings = getattr(request.app.state, "hotkey_settings", None)
    if settings is None:
        return VoiceHotkeySettings()
    return settings


VoiceHotkeySettingsDep = Annotated[VoiceHotkeySettings, Depends(get_voice_hotkey_settings)]


@router.get("/settings/hotkey")
def get_voice_hotkey(settings: VoiceHotkeySettingsDep) -> VoiceHotkeyResponse:
    return VoiceHotkeyResponse(hotkey=settings.spec)


@router.put("/settings/hotkey")
def update_voice_hotkey(
    body: VoiceHotkeyBody,
    settings: VoiceHotkeySettingsDep,
    request: Request,
) -> VoiceHotkeyResponse:
    try:
        binding = HotkeyBinding.parse(body.hotkey)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    previous = settings.binding
    settings.set_binding(binding)

    hotkey_service: VoiceHotkeyService | None = getattr(
        request.app.state,
        "hotkey_service",
        None,
    )
    if hotkey_service is None:
        return VoiceHotkeyResponse(hotkey=settings.spec)

    try:
        hotkey_service.rebind()
    except HotkeyRegistrationError as exc:
        settings.set_binding(previous)
        try:
            hotkey_service.rebind()
        except HotkeyRegistrationError:
            pass
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return VoiceHotkeyResponse(hotkey=settings.spec)
