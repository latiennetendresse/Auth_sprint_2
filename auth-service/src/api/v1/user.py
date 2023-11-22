from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from core.logging import LoggingRoute
from schemas.base import HTTPExceptionResponse
from schemas.users import UserPatch, UserResponse
from services.user import UserService, get_user_service

router = APIRouter(route_class=LoggingRoute)

get_token = HTTPBearer(auto_error=False)


@router.get(
    "",
    response_model=UserResponse,
    summary="Данные профиля",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
    },
)
async def get_current_user(
    access_token: str = Depends(get_token),
    auth_jwt: AuthJWT = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    await auth_jwt.jwt_required()
    user = await user_service.get_current_user()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch(
    "",
    response_model=UserResponse,
    summary="Изменение данных профиля",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
    },
)
async def patch_current_user(
    user_patch: UserPatch,
    access_token: str = Depends(get_token),
    auth_jwt: AuthJWT = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    await auth_jwt.jwt_required()
    user = await user_service.patch_current_user(user_patch)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
