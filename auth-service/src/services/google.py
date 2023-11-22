import logging
from functools import lru_cache

import httpx
from fastapi import Depends, status
from pydantic import HttpUrl

from core.settings import settings
from services.social import SocialService, get_social_service
from utils.http import get_http_client

logger = logging.getLogger(__name__)


class GoogleService:
    def __init__(self, http_client: httpx.AsyncClient, social_service: SocialService):
        self.http_client = http_client
        self.social_service = social_service

    async def get_user(self, code: str, redirect_uri: HttpUrl):
        try:
            response = await self.http_client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": redirect_uri,
                    "code": code,
                    "grant_type": "authorization_code",
                },
            )
        except httpx.HTTPError:
            return None

        if response.status_code != status.HTTP_200_OK:
            return None

        data = response.json()
        access_token = data.get("access_token")

        try:
            response = await self.http_client.get(
                "https://www.googleapis.com/userinfo/v2/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        except httpx.HTTPError:
            return None

        if response.status_code != status.HTTP_200_OK:
            return None

        data = response.json()
        social_id = data.get("id")
        email = data.get("email")
        name = data.get("name")
        return await self.social_service.get_user(social_id, "google", email, name)


@lru_cache()
def get_google_service(
    http_client: httpx.AsyncClient = Depends(get_http_client),
    social_service: SocialService = Depends(get_social_service),
) -> GoogleService:
    return GoogleService(http_client, social_service)
