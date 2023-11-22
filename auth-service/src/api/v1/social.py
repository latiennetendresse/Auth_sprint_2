import logging
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Header, HTTPException, Path, status
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from core.logging import LoggingRoute
from core.settings import settings
from schemas.base import HTTPExceptionResponse
from services.auth import AuthService, get_auth_service
from services.google import GoogleService, get_google_service
from services.vk import VKService, get_vk_service
from services.yandex import YandexService, get_yandex_service
from utils.random import generate_random_string

logger = logging.getLogger(__name__)

router = APIRouter(route_class=LoggingRoute)


@router.get(
    "/{social_name}/login",
    summary="Редирект на вход через соц.сети",
    response_class=RedirectResponse,
)
async def login(
    social_name: Annotated[
        Literal["google", "vk", "yandex"], Path(description="OAuth2 провайдер")
    ],
    request: Request,
) -> RedirectResponse:
    redirect_uri = request.url_for("auth", social_name=social_name)
    state = generate_random_string(16)
    request.session["state"] = state

    if social_name == "vk":
        return RedirectResponse(
            f"https://oauth.vk.com/authorize?client_id={settings.vk_client_id}&"
            f"redirect_uri={redirect_uri}&display=page&scope=4194304&state={state}"
        )
    elif social_name == "google":
        return RedirectResponse(
            f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&"
            f"client_id={settings.google_client_id}&redirect_uri={redirect_uri}&"
            f"scope=https://www.googleapis.com/auth/userinfo.email+"
            f"https://www.googleapis.com/auth/userinfo.profile&state={state}"
        )
    elif social_name == "yandex":
        return RedirectResponse(
            f"https://oauth.yandex.ru/authorize"
            f"?response_type=code"
            f"&client_id={settings.yandex_client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
        )


@router.get(
    "/{social_name}/auth",
    summary="Обмен кода подтверждения от соц.сети на токены",
    description="В случае успеха делает редирект на фронтенд, а токены для "
    "доступа к API передаёт через cookies.",
    response_class=RedirectResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionResponse}},
)
async def auth(
    social_name: Annotated[
        Literal["google", "vk", "yandex"], Path(description="OAuth2 провайдер")
    ],
    code: str,
    state: str,
    request: Request,
    user_agent: Annotated[str | None, Header(include_in_schema=False)] = None,
    google_service: GoogleService = Depends(get_google_service),
    vk_service: VKService = Depends(get_vk_service),
    auth_service: AuthService = Depends(get_auth_service),
    yandex_service: YandexService = Depends(get_yandex_service),
) -> RedirectResponse:
    if state != request.session["state"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="State check failed"
        )

    redirect_uri = request.url_for("auth", social_name=social_name)

    user = None
    if social_name == "vk":
        user = await vk_service.get_user(code, redirect_uri)
    elif social_name == "google":
        user = await google_service.get_user(code, redirect_uri)
    elif social_name == "yandex":
        user = await yandex_service.get_user(code)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    redirect = RedirectResponse(url=settings.frontend_redirect_url)
    response = await auth_service.login(user, user_agent)
    redirect.set_cookie("user_id", response.user_id)
    redirect.set_cookie("access_token", response.access_token)
    redirect.set_cookie("refresh_token", response.refresh_token)
    return redirect
