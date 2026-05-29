import asyncio
import logging
from typing import Any

from starlette.websockets import WebSocket

logger = logging.getLogger(__name__)


class WebSocketConnectionManager:
    """Tracks active WebSocket clients and broadcasts JSON messages."""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    @property
    def client_count(self) -> int:
        return len(self._connections)

    def has_clients(self) -> bool:
        return bool(self._connections)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def send_json(self, websocket: WebSocket, message: dict[str, Any]) -> bool:
        try:
            await websocket.send_json(message)
            return True
        except Exception:
            logger.debug("Failed to send to websocket client", exc_info=True)
            await self.disconnect(websocket)
            return False

    async def broadcast(self, message: dict[str, Any]) -> None:
        if not self._connections:
            return

        async with self._lock:
            clients = list(self._connections)

        dead: list[WebSocket] = []
        for websocket in clients:
            try:
                await websocket.send_json(message)
            except Exception:
                logger.debug("Failed to broadcast to client", exc_info=True)
                dead.append(websocket)

        for websocket in dead:
            await self.disconnect(websocket)
