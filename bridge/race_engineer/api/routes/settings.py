from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from race_engineer.ai.prompt.models import PersonalityMode
from race_engineer.proactive.triggers.models import TriggerType
from race_engineer.settings.cooldown import CooldownSettings, validate_cooldown_interval
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


class CooldownSettingsBody(BaseModel):
    global_interval_seconds: float | None = Field(
        default=None,
        ge=0.0,
        description="Minimum seconds between any proactive trigger messages",
    )
    trigger_intervals_seconds: dict[str, float] | None = Field(
        default=None,
        description="Per-trigger cooldowns keyed by trigger type",
    )


class CooldownSettingsResponse(BaseModel):
    global_interval_seconds: float
    trigger_intervals_seconds: dict[str, float]


def get_cooldown_settings(request: Request) -> CooldownSettings:
    settings = getattr(request.app.state, "cooldown_settings", None)
    if settings is None:
        return CooldownSettings()
    return settings


CooldownSettingsDep = Annotated[CooldownSettings, Depends(get_cooldown_settings)]


def _cooldown_response(settings: CooldownSettings) -> CooldownSettingsResponse:
    config = settings.config
    return CooldownSettingsResponse(
        global_interval_seconds=config.global_interval_seconds,
        trigger_intervals_seconds={
            trigger_type.value: interval
            for trigger_type, interval in config.trigger_intervals_seconds.items()
        },
    )


@router.get("/settings/cooldown")
def get_cooldown(settings: CooldownSettingsDep) -> CooldownSettingsResponse:
    return _cooldown_response(settings)


@router.put("/settings/cooldown")
def update_cooldown(
    body: CooldownSettingsBody,
    settings: CooldownSettingsDep,
) -> CooldownSettingsResponse:
    trigger_intervals: dict[TriggerType, float] | None = None
    if body.trigger_intervals_seconds is not None:
        trigger_intervals = {}
        for key, value in body.trigger_intervals_seconds.items():
            try:
                trigger_type = TriggerType(key)
            except ValueError as exc:
                raise HTTPException(
                    status_code=422,
                    detail=f"unknown trigger type: {key}",
                ) from exc
            try:
                trigger_intervals[trigger_type] = validate_cooldown_interval(value)
            except ValueError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc

    global_interval = body.global_interval_seconds
    if global_interval is not None:
        try:
            global_interval = validate_cooldown_interval(global_interval)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    settings.update(
        global_interval_seconds=global_interval,
        trigger_intervals_seconds=trigger_intervals,
    )
    return _cooldown_response(settings)
