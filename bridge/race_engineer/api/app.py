from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from race_engineer.api.config import get_cors_origins, load_env
from race_engineer.api.routes.health import router as health_router
from race_engineer.api.routes.voice import router as voice_router
from race_engineer.api.routes.ws import router as ws_router
from race_engineer.api.ws import TelemetryBroadcaster, WebSocketConnectionManager
from race_engineer.connection import SdkConnectionService
from race_engineer.session import SessionInfoReader
from race_engineer.position import PositionCalculator
from race_engineer.standings import StandingsReader
from race_engineer.fuel import FuelConsumptionTracker
from race_engineer.storage.database import connect
from race_engineer.storage.fuel_repository import FuelLapRepository
from race_engineer.telemetry import TelemetryVariableReader
from race_engineer.voice.pipeline import VoicePipeline
from race_engineer.voice.stt.client import ElevenLabsSttClient
from race_engineer.voice.stt.config import load_elevenlabs_stt_config


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    connection_service = app.state.connection_service
    broadcaster = app.state.broadcaster
    await broadcaster.start()
    try:
        yield
    finally:
        await broadcaster.stop()
        connection_service.disconnect()


def create_app(
    connection_service: SdkConnectionService | None = None,
    ws_manager: WebSocketConnectionManager | None = None,
    broadcaster: TelemetryBroadcaster | None = None,
    voice_pipeline: VoicePipeline | None = None,
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
    fuel_tracker = FuelConsumptionTracker(repository=fuel_repository)
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
        )

    app.state.connection_service = resolved_connection_service
    app.state.ws_manager = resolved_ws_manager
    app.state.broadcaster = resolved_broadcaster
    app.state.voice_pipeline = voice_pipeline or _build_voice_pipeline()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(voice_router)
    app.include_router(ws_router)
    return app


def _build_voice_pipeline() -> VoicePipeline | None:
    config = load_elevenlabs_stt_config()
    if config is None:
        return None
    return VoicePipeline(ElevenLabsSttClient(config))


load_env()
app = create_app()
