from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from core.logging import LoggingRoute
from schemas.base import HTTPExceptionResponse
from schemas.roles import RoleBase, RoleResponse
from services.auth import AuthService, get_auth_service
from services.role import RoleService, get_role_service

router = APIRouter(route_class=LoggingRoute)

get_token = HTTPBearer(auto_error=False)


@router.get(
    "",
    response_model=list[RoleResponse],
    summary="Список ролей",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
    },
)
async def list_roles(
    access_token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
    role_service: RoleService = Depends(get_role_service),
) -> list[RoleResponse]:
    await auth_service.check_access(["admin"])
    return await role_service.list_roles()


@router.post(
    "",
    response_model=RoleResponse,
    summary="Создание роли",
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": HTTPExceptionResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
    },
)
async def create_role(
    role_create: RoleBase,
    access_token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
    role_service: RoleService = Depends(get_role_service),
) -> RoleResponse:
    await auth_service.check_access(["admin"])
    if await role_service.get_role_by_name(role_create.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists"
        )
    return await role_service.create_role(role_create)


@router.patch(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Изменение роли",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
    },
)
async def patch_role(
    role_id: UUID,
    role_patch: RoleBase,
    access_token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
    role_service: RoleService = Depends(get_role_service),
) -> RoleResponse:
    await auth_service.check_access(["admin"])
    role = await role_service.patch_role(role_id, role_patch)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление роли",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse},
        status.HTTP_403_FORBIDDEN: {"model": HTTPExceptionResponse},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionResponse},
    },
)
async def delete_role(
    role_id: UUID,
    access_token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
    role_service: RoleService = Depends(get_role_service),
) -> None:
    await auth_service.check_access(["admin"])
    if not (await role_service.delete_role(role_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
