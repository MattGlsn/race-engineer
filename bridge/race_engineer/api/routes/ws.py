from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request

from race_engineer.api.ws.manager import WebSocketConnectionManager
from race_engineer.api.ws.messages import build_connection_message
from race_engineer.connection import SdkConnectionService

router = APIRouter(tags=["websocket"])


def _get_ws_manager(request: Request) -> WebSocketConnectionManager:
    return request.app.state.ws_manager


def _get_connection_service(request: Request) -> SdkConnectionService:
    return request.app.state.connection_service


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    manager = _get_ws_manager(websocket)
    connection_service = _get_connection_service(websocket)

    await manager.connect(websocket)
    try:
        await manager.send_json(
            websocket,
            build_connection_message(connection_service.as_dict()),
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket)
