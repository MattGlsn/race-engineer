from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from race_engineer.api.config import get_cors_origins
from race_engineer.api.routes.health import router as health_router
from race_engineer.api.routes.ws import router as ws_router
from race_engineer.api.ws import WebSocketConnectionManager
from race_engineer.connection import SdkConnectionService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    connection_service = app.state.connection_service
    yield
    connection_service.disconnect()


def create_app(connection_service: SdkConnectionService | None = None) -> FastAPI:
    app = FastAPI(
        title="Race Engineer Bridge API",
        description="Telemetry bridge API for iRacing",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.connection_service = (
        connection_service if connection_service is not None else SdkConnectionService()
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.ws_manager = WebSocketConnectionManager()
    app.include_router(health_router)
    app.include_router(ws_router)
    return app


app = create_app()
