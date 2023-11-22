from typing import Annotated, Optional
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer

from core.logging import LoggingRoute
from schemas.base import HTTPExceptionResponse
from schemas.sessions import SessionResponse
from services.session import SessionService, get_session_service

router = APIRouter(route_class=LoggingRoute)

get_token = HTTPBearer(auto_error=False)


@router.get(
    "",
    response_model=list[SessionResponse],
    summary="История входов в аккаунт",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse}},
)
async def list_user_sessions(
    access_token: Annotated[str, Depends(get_token)],
    active: Annotated[Optional[bool], Query(description="Сессия активна")] = None,
    page_size: Annotated[int, Query(description="Размер страницы", ge=1)] = 20,
    page_number: Annotated[int, Query(description="Номер страницы", ge=1)] = 1,
    auth_jwt: AuthJWT = Depends(),
    session_service: SessionService = Depends(get_session_service),
) -> list[SessionResponse]:
    await auth_jwt.jwt_required()
    return await session_service.list_user_sessions(active, page_size, page_number)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Завершение сессии",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
    },
)
async def end_user_session(
    session_id: UUID,
    access_token: Annotated[str, Depends(get_token)],
    auth_jwt: AuthJWT = Depends(),
    session_service: SessionService = Depends(get_session_service),
) -> None:
    await auth_jwt.jwt_required()
    if not (await session_service.end_user_session(session_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
