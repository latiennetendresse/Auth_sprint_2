import logging
from functools import lru_cache

import httpx
from fastapi import Depends, status
from pydantic import HttpUrl

from core.settings import settings
from services.social import SocialService, get_social_service
from utils.http import get_http_client

logger = logging.getLogger(__name__)


class VKService:
    def __init__(self, http_client: httpx.AsyncClient, social_service: SocialService):
        self.http_client = http_client
        self.social_service = social_service

    async def get_user(self, code: str, redirect_uri: HttpUrl):
        try:
            response = await self.http_client.get(
                "https://oauth.vk.com/access_token",
                params={
                    "client_id": settings.vk_client_id,
                    "client_secret": settings.vk_client_secret,
                    "redirect_uri": redirect_uri,
                    "code": code,
                    "v": "5.154",
                },
            )
        except httpx.HTTPError:
            return None

        if response.status_code != status.HTTP_200_OK:
            return None

        data = response.json()
        access_token = data.get("access_token")
        email = data.get("email")
        social_id = str(data.get("user_id"))
        name = await self.get_user_name(access_token)
        return await self.social_service.get_user(social_id, "vk", email, name)

    async def get_user_name(self, access_token: str) -> str:
        try:
            response = await self.http_client.get(
                "https://api.vk.com/method/users.get",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"v": "5.154"},
            )
        except httpx.HTTPError:
            return ""

        if response.status_code != status.HTTP_200_OK:
            return ""

        try:
            data = response.json()["response"][0]
            return f'{data["first_name"]} {data["last_name"]}'
        except (IndexError, KeyError):
            return ""


@lru_cache()
def get_vk_service(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    social_service: SocialService = Depends(get_social_service),
) -> VKService:
    return VKService(http_client, social_service)
