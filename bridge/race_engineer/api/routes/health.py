from fastapi import APIRouter

from race_engineer.api.dependencies import ConnectionServiceDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health(connection_service: ConnectionServiceDep) -> dict:
    if connection_service.is_connected:
        connection_service.check_health()

    return {
        "status": "ok",
        "connection": connection_service.as_dict(),
    }
