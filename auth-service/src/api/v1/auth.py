from typing import Annotated, Literal

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import MissingTokenError
from fastapi import APIRouter, Body, Depends, Header, HTTPException, Query, status
from fastapi.security import HTTPBearer

from core.logging import LoggingRoute
from schemas.auth import Credentials, LoginResponse, TokenPair
from schemas.base import HTTPExceptionResponse
from services.auth import AuthService, get_auth_service

router = APIRouter(route_class=LoggingRoute)

get_token = HTTPBearer(auto_error=False)


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Вход",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse}},
)
async def login(
    credentials: Credentials,
    user_agent: Annotated[str | None, Header(include_in_schema=False)] = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    user = await auth_service.get_user(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad username or password"
        )
    return await auth_service.login(user, user_agent)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Выход",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse}},
)
async def logout(
    access_token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.check_access()
    await auth_service.logout()


@router.post(
    "/refresh_tokens",
    response_model=TokenPair,
    summary="Обновление токенов",
    responses={status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse}},
)
async def refresh_tokens(
    refresh_token: Annotated[str, Body(embed=True)],
    auth_jwt: AuthJWT = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    try:
        await auth_jwt.jwt_refresh_token_required(
            auth_from="websocket", token=refresh_token
        )
    except MissingTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )

    tokens = await auth_service.refresh_tokens(refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No active session"
        )

    return tokens


@router.get(
    "/check_access",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Проверка доступа",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
    },
)
async def check_access(
    access_token: Annotated[str, Depends(get_token)],
    allow_roles: Annotated[
        list[Literal["admin", "subscriber"]], Query(description="Кому доступно")
    ] = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.check_access(allow_roles)
