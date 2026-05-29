from typing import Annotated

from fastapi import Depends, Request

from race_engineer.connection import SdkConnectionService


def get_connection_service(request: Request) -> SdkConnectionService:
    return request.app.state.connection_service


ConnectionServiceDep = Annotated[SdkConnectionService, Depends(get_connection_service)]
