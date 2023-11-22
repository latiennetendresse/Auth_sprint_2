import logging
from functools import lru_cache

import httpx
from fastapi import Depends, status

from core.settings import settings
from models.users import User
from services.social import SocialService, get_social_service
from utils.http import get_http_client

logger = logging.getLogger(__name__)


class YandexService:
    def __init__(self, social_service: SocialService, http_client: httpx.AsyncClient):
        self.social_service = social_service
        self.http_client = http_client

    async def get_user(self, code) -> User:
        try:
            response = await self.http_client.post(
                "https://oauth.yandex.ru/token",
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "client_id": settings.yandex_client_id,
                    "client_secret": settings.yandex_client_secret,
                },
            )

            if response.status_code != status.HTTP_200_OK:
                return None

            data = response.json()
            access_token = data.get("access_token")

            user_info_response = await self.http_client.get(
                "https://login.yandex.ru/info",
                headers={"Authorization": f"OAuth {access_token}"},
            )

            if user_info_response.status_code != status.HTTP_200_OK:
                return None

            user_data = user_info_response.json()

        except httpx.HTTPError:
            return None

        return await self.social_service.get_user(
            social_id=user_data.get("psuid"),
            social_name="yandex",
            email=user_data.get("default_email"),
            name=user_data.get("real_name", ""),
        )


@lru_cache()
def get_yandex_service(
    social_service: SocialService = Depends(get_social_service),
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> YandexService:
    return YandexService(social_service, http_client)
