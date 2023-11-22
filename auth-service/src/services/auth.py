import logging
from datetime import datetime
from functools import lru_cache
from typing import Optional
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import settings
from db.postgres import get_session
from db.redis import get_redis
from models.sessions import Session
from models.users import User
from schemas.auth import Credentials, LoginResponse, TokenPair

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis, auth_jwt: AuthJWT):
        self.db = db
        self.redis = redis
        self.auth_jwt = auth_jwt

    async def get_user(self, credentials: Credentials) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == credentials.username)
        )
        user = result.scalars().first()
        if not user or not user.check_password(credentials.password):
            return None
        return user

    async def login(
        self, user: User, user_agent: Optional[str]
    ) -> Optional[LoginResponse]:
        session = Session(user_id=user.id, user_agent=user_agent)
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        tokens = await self.create_token_pair(user, session.id)
        return LoginResponse(
            user_id=user.id,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
        )

    async def logout(self) -> None:
        access_jwt = await self.auth_jwt.get_raw_jwt()
        await self.end_session(access_jwt["session_id"], "logout")

    async def refresh_tokens(self, refresh_token: str) -> Optional[TokenPair]:
        refresh_jwt = await self.auth_jwt.get_raw_jwt(refresh_token)
        result = await self.db.execute(
            select(Session).where(Session.id == refresh_jwt["session_id"])
        )
        session = result.scalars().first()

        if not session or session.session_exp < datetime.utcnow():
            return None

        # Токен валидный, но используется повторно?
        if str(session.refresh_jti) != refresh_jwt["jti"]:
            await self.end_session(session.id, "refresh")
            return None

        await self.revoke_access_token(session.access_jti, "refresh")

        user = await self.db.get(User, session.user_id)
        return await self.create_token_pair(user, session.id)

    async def end_session(self, session_id: UUID, reason: str):
        result = await self.db.execute(
            update(Session)
            .where(Session.id == session_id)
            .values(session_exp=datetime.utcnow())
            .returning(Session)
        )
        await self.db.commit()

        session = result.first()
        if session:
            await self.revoke_access_token(session.access_jti, reason)

    async def revoke_access_token(self, jti: UUID, reason: str):
        await self.redis.setex(str(jti), settings.authjwt_access_token_expires, reason)

    async def revoke_all_access_tokens(self, user_id: UUID, reason: str):
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id)
        )
        for session in result.scalars().all():
            await self.revoke_access_token(session.access_jti, reason)

    async def create_token_pair(self, user: User, session_id: UUID) -> TokenPair:
        roles = [user_role.role.name for user_role in user.roles]
        access_token = await self.auth_jwt.create_access_token(
            subject=str(user.id),
            user_claims={"session_id": str(session_id), "roles": roles},
        )
        refresh_token = await self.auth_jwt.create_refresh_token(
            subject=str(user.id), user_claims={"session_id": str(session_id)}
        )
        refresh_jwt = await self.auth_jwt.get_raw_jwt(refresh_token)

        statement = (
            update(Session)
            .where(Session.id == session_id)
            .values(
                {
                    "access_jti": await self.auth_jwt.get_jti(access_token),
                    "refresh_jti": refresh_jwt["jti"],
                    "session_exp": datetime.fromtimestamp(refresh_jwt["exp"]),
                }
            )
        )
        await self.db.execute(statement)
        await self.db.commit()

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def check_access(self, allow_roles: list[str] = None) -> None:
        await self.auth_jwt.jwt_required()

        if allow_roles is None:
            return

        access_jwt = await self.auth_jwt.get_raw_jwt()
        if not set(allow_roles) & set(access_jwt["roles"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )


@lru_cache()
def get_auth_service(
    db: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
    auth_jwt: AuthJWT = Depends(),
) -> AuthService:
    return AuthService(db, redis, auth_jwt)
