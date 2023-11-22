from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from core.logging import LoggingRoute
from schemas.base import HTTPExceptionResponse
from services.auth import AuthService, get_auth_service
from services.user_role import UserRoleService, get_user_role_service

router = APIRouter(route_class=LoggingRoute)

get_token = HTTPBearer(auto_error=False)


@router.post(
    "/{user_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Добавление роли пользователю",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": HTTPExceptionResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
    },
)
async def create_user_role(
    user_id: UUID,
    role_id: Annotated[UUID, Body(embed=True)],
    access_token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> None:
    await auth_service.check_access(["admin"])
    if not await user_role_service.get_user_by_id(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )
    if not await user_role_service.get_role_by_id(role_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found"
        )
    if await user_role_service.get_user_role(user_id, role_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User role already exists"
        )
    await user_role_service.create_user_role(user_id, role_id)


@router.delete(
    "/{user_id}/roles",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление роли у пользователя",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
    },
)
async def delete_user_role(
    user_id: UUID,
    role_id: Annotated[UUID, Body(embed=True)],
    access_token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
    user_role_service: UserRoleService = Depends(get_user_role_service),
) -> None:
    await auth_service.check_access(["admin"])
    if not await user_role_service.delete_user_role(user_id, role_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User role not found"
        )
