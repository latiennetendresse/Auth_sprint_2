import logging
from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.roles import Role, UserRole
from models.users import User
from services.auth import AuthService, get_auth_service

logger = logging.getLogger(__name__)


class UserRoleService:
    def __init__(self, db: AsyncSession, auth_service: AuthService):
        self.db = db
        self.auth_service = auth_service

    async def get_user_by_id(self, user_id: UUID) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_role_by_id(self, role_id: UUID) -> Role:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalars().first()

    async def get_user_role(self, user_id: UUID, role_id: UUID) -> UserRole:
        result = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id, UserRole.role_id == role_id
            )
        )
        return result.scalars().first()

    async def create_user_role(self, user_id: UUID, role_id: UUID) -> None:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(user_role)
        await self.db.commit()
        await self.auth_service.revoke_all_access_tokens(user_id, "add_role")

    async def delete_user_role(self, user_id: UUID, role_id: UUID) -> bool:
        result = await self.db.execute(
            delete(UserRole).where(
                UserRole.role_id == role_id, UserRole.user_id == user_id
            )
        )
        await self.db.commit()
        await self.auth_service.revoke_all_access_tokens(user_id, "delete_role")
        return result.rowcount


@lru_cache()
def get_user_role_service(
    db: AsyncSession = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRoleService:
    return UserRoleService(db, auth_service)
