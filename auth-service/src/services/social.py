import logging
from functools import lru_cache

from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from models.social import SocialAccount
from models.users import User
from utils.random import generate_random_string

logger = logging.getLogger(__name__)


class SocialService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(
        self, social_id: str, social_name: str, email: EmailStr, name: str
    ) -> User:
        result = await self.db.execute(
            select(SocialAccount).where(
                SocialAccount.social_id == social_id,
                SocialAccount.social_name == social_name,
            )
        )
        social_account = result.scalars().first()
        if social_account:
            result = await self.db.execute(
                select(User).where(User.id == social_account.user_id)
            )
            return result.scalars().first()

        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user:
            user = User(email, generate_random_string(16), name)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

        social_account = SocialAccount(
            user_id=user.id,
            social_id=social_id,
            social_name=social_name,
        )
        self.db.add(social_account)
        await self.db.commit()

        return user


@lru_cache()
def get_social_service(
    db: AsyncSession = Depends(get_session),
) -> SocialService:
    return SocialService(db)
