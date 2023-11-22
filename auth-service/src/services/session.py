import logging
from datetime import datetime
from functools import lru_cache
from typing import Optional
from uuid import UUID

from async_fastapi_jwt_auth import AuthJWT
from fastapi import Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.sessions import Session
from schemas.sessions import SessionResponse
from services.auth import AuthService, get_auth_service

logger = logging.getLogger(__name__)


class SessionService:
    def __init__(self, db: AsyncSession, auth_jwt: AuthJWT, auth_service: AuthService):
        self.db = db
        self.auth_jwt = auth_jwt
        self.auth_service = auth_service

    async def list_user_sessions(
        self, active: Optional[bool], page_size: int, page_number: int
    ) -> list[SessionResponse]:
        user_id = await self.auth_jwt.get_jwt_subject()
        filters = [Session.user_id == user_id]

        if active:
            filters.append(
                or_(
                    Session.session_exp >= datetime.utcnow(),
                    Session.session_exp.is_(None),
                )
            )
        elif active is not None:
            filters.append(Session.session_exp < datetime.utcnow())

        result = await self.db.execute(
            select(Session)
            .where(*filters)
            .order_by(Session.created_at.desc())
            .limit(page_size)
            .offset(page_size * (page_number - 1))
        )
        return result.scalars().all()

    async def end_user_session(self, session_id: UUID) -> bool:
        user_id = await self.auth_jwt.get_jwt_subject()
        result = await self.db.execute(
            select(Session).where(Session.user_id == user_id, Session.id == session_id)
        )
        session = result.scalars().first()

        if not session:
            return False

        await self.auth_service.end_session(session.id, "end_user_session")
        return True


@lru_cache()
def get_session_service(
    db: AsyncSession = Depends(get_session),
    auth_jwt: AuthJWT = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> SessionService:
    return SessionService(db, auth_jwt, auth_service)
