import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from race_engineer.api.config import get_cors_origins, load_env
from race_engineer.api.routes.health import router as health_router
from race_engineer.api.routes.settings import router as settings_router
from race_engineer.api.routes.voice import router as voice_router
from race_engineer.api.routes.ws import router as ws_router
from race_engineer.api.ws import TelemetryBroadcaster, WebSocketConnectionManager
from race_engineer.ai.llm.client import OpenAiChatClient
from race_engineer.ai.llm.config import load_openai_llm_config
from race_engineer.ai.service import EngineerAiService
from race_engineer.context.aggregator import ContextAggregator
from race_engineer.coaching.trace import TraceRecorder
from race_engineer.connection import SdkConnectionService
from race_engineer.session import SessionInfoReader
from race_engineer.position import PositionCalculator
from race_engineer.standings import StandingsReader
from race_engineer.fuel import FuelConsumptionTracker
from race_engineer.storage.database import connect
from race_engineer.storage.fuel_repository import FuelLapRepository
from race_engineer.storage.trace_repository import TraceRepository
from race_engineer.telemetry import TelemetryVariableReader
from race_engineer.voice.engineer import EngineerVoiceService
from race_engineer.voice.pipeline import VoicePipeline
from race_engineer.voice.stt.client import ElevenLabsSttClient
from race_engineer.voice.stt.config import load_elevenlabs_stt_config
from race_engineer.voice.tts.client import ElevenLabsTtsClient
from race_engineer.voice.tts.config import load_elevenlabs_tts_config
from race_engineer.voice.audio.volume import load_voice_volume_config
from race_engineer.voice.conversation.orchestrator import VoiceConversationOrchestrator
from race_engineer.voice.hotkey.errors import HotkeyRegistrationError
from race_engineer.voice.hotkey.service import VoiceHotkeyService
from race_engineer.settings.hotkey import VoiceHotkeySettings
from race_engineer.settings.personality import PersonalitySettings
from race_engineer.settings.volume import VoiceVolumeSettings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    connection_service = app.state.connection_service
    broadcaster = app.state.broadcaster
    hotkey_service: VoiceHotkeyService | None = app.state.hotkey_service
    connection_service.connect()
    await broadcaster.start()
    if hotkey_service is not None:
        try:
            hotkey_service.start(asyncio.get_running_loop())
        except HotkeyRegistrationError:
            logger.exception("voice hotkey listener failed to start")
    try:
        yield
    finally:
        if hotkey_service is not None:
            hotkey_service.stop()
        await broadcaster.stop()
        connection_service.disconnect()


def create_app(
    connection_service: SdkConnectionService | None = None,
    ws_manager: WebSocketConnectionManager | None = None,
    broadcaster: TelemetryBroadcaster | None = None,
    voice_pipeline: VoicePipeline | None = None,
    engineer_voice: EngineerVoiceService | None = None,
    engineer_ai: EngineerAiService | None = None,
    context_aggregator: ContextAggregator | None = None,
    hotkey_service: VoiceHotkeyService | None = None,
    personality_settings: PersonalitySettings | None = None,
    voice_volume_settings: VoiceVolumeSettings | None = None,
    hotkey_settings: VoiceHotkeySettings | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Race Engineer Bridge API",
        description="Telemetry bridge API for iRacing",
        version="0.1.0",
        lifespan=lifespan,
    )
    resolved_connection_service = (
        connection_service if connection_service is not None else SdkConnectionService()
    )
    resolved_ws_manager = (
        ws_manager if ws_manager is not None else WebSocketConnectionManager()
    )
    sdk = resolved_connection_service.sdk
    db_connection = connect()
    fuel_repository = FuelLapRepository(db_connection)
    trace_repository = TraceRepository(db_connection)
    fuel_tracker = FuelConsumptionTracker(repository=fuel_repository)
    trace_recorder = TraceRecorder(repository=trace_repository)
    resolved_broadcaster = broadcaster
    if resolved_broadcaster is None:
        resolved_broadcaster = TelemetryBroadcaster(
            resolved_ws_manager,
            resolved_connection_service,
            TelemetryVariableReader(sdk=sdk),
            SessionInfoReader(sdk=sdk),
            StandingsReader(sdk=sdk),
            PositionCalculator(sdk=sdk),
            fuel_tracker=fuel_tracker,
            trace_recorder=trace_recorder,
        )

    resolved_voice_pipeline = voice_pipeline or _build_voice_pipeline()
    resolved_context_aggregator = context_aggregator or ContextAggregator(
        resolved_connection_service,
        fuel_tracker=fuel_tracker,
        fuel_repository=fuel_repository,
    )
    resolved_voice_volume_settings = voice_volume_settings or VoiceVolumeSettings(
        load_voice_volume_config().volume
    )
    resolved_engineer_voice = engineer_voice or _build_engineer_voice(
        resolved_voice_volume_settings
    )
    resolved_engineer_ai = engineer_ai or _build_engineer_ai()
    resolved_personality_settings = personality_settings or PersonalitySettings()
    resolved_hotkey_settings = hotkey_settings or VoiceHotkeySettings.from_env()

    app.state.connection_service = resolved_connection_service
    app.state.ws_manager = resolved_ws_manager
    app.state.broadcaster = resolved_broadcaster
    app.state.voice_pipeline = resolved_voice_pipeline
    app.state.engineer_voice = resolved_engineer_voice
    app.state.engineer_ai = resolved_engineer_ai
    app.state.context_aggregator = resolved_context_aggregator
    app.state.personality_settings = resolved_personality_settings
    app.state.voice_volume_settings = resolved_voice_volume_settings
    app.state.hotkey_settings = resolved_hotkey_settings
    app.state.hotkey_service = hotkey_service or _build_hotkey_service(
        resolved_voice_pipeline,
        resolved_ws_manager,
        resolved_context_aggregator,
        resolved_engineer_ai,
        resolved_engineer_voice,
        resolved_personality_settings,
        resolved_hotkey_settings,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(settings_router)
    app.include_router(voice_router)
    app.include_router(ws_router)
    return app


def _build_voice_pipeline() -> VoicePipeline | None:
    config = load_elevenlabs_stt_config()
    if config is None:
        return None
    return VoicePipeline(ElevenLabsSttClient(config))


def _build_hotkey_service(
    voice_pipeline: VoicePipeline | None,
    ws_manager: WebSocketConnectionManager,
    context_aggregator: ContextAggregator,
    engineer_ai: EngineerAiService | None,
    engineer_voice: EngineerVoiceService | None,
    personality_settings: PersonalitySettings,
    hotkey_settings: VoiceHotkeySettings,
) -> VoiceHotkeyService | None:
    if voice_pipeline is None:
        return None
    orchestrator = VoiceConversationOrchestrator(
        ws_manager,
        context_aggregator,
        engineer_ai,
        engineer_voice,
        personality_settings=personality_settings,
    )
    return VoiceHotkeyService(
        voice_pipeline,
        ws_manager=ws_manager,
        hotkey_settings=hotkey_settings,
        orchestrator=orchestrator,
    )


def _build_engineer_voice(
    voice_volume_settings: VoiceVolumeSettings,
) -> EngineerVoiceService | None:
    config = load_elevenlabs_tts_config()
    if config is None:
        return None
    return EngineerVoiceService(
        ElevenLabsTtsClient(config),
        volume_settings=voice_volume_settings,
    )


def _build_engineer_ai() -> EngineerAiService | None:
    config = load_openai_llm_config()
    if config is None:
        return None
    return EngineerAiService(OpenAiChatClient(config))


load_env()
app = create_app()
