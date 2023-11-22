import logging
from functools import lru_cache
from typing import Optional

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash

from db.postgres import get_session
from models.users import User
from schemas.users import UserCreate, UserPatch, UserResponse

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession, auth_jwt: AuthJWT):
        self.db = db
        self.auth_jwt = auth_jwt

    async def get_user_by_email(self, email: EmailStr) -> Optional[UserResponse]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create_user(self, user_create: UserCreate) -> UserResponse:
        user = User(**jsonable_encoder(user_create))
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_current_user(self) -> Optional[UserResponse]:
        user_id = await self.auth_jwt.get_jwt_subject()
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def patch_current_user(self, user_patch: UserPatch) -> Optional[UserResponse]:
        user_id = await self.auth_jwt.get_jwt_subject()
        values = jsonable_encoder(user_patch, exclude_unset=True)
        if password := values.pop("password", None):
            values["password_hash"] = generate_password_hash(password)
        result = await self.db.execute(
            update(User).where(User.id == user_id).values(**values).returning(User)
        )
        await self.db.commit()
        return result.first()


@lru_cache()
def get_user_service(
    db: AsyncSession = Depends(get_session), auth_jwt: AuthJWT = Depends()
) -> UserService:
    return UserService(db, auth_jwt)
