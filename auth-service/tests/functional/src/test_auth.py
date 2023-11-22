from http import HTTPStatus

import pytest
from aiohttp import hdrs

pytestmark = pytest.mark.asyncio


async def test_login(login, ivanov, check_access, refresh_tokens):
    response = await login("ivanov@ya.ru", "qwerty")
    assert response["status"] == HTTPStatus.OK
    tokens = response["body"]

    response = await check_access(tokens["access_token"])
    assert response["status"] == HTTPStatus.NO_CONTENT

    response = await refresh_tokens(tokens["refresh_token"])
    assert response["status"] == HTTPStatus.OK


@pytest.mark.parametrize(
    "credentials",
    [
        ({"username": "ivanov@ya.ru", "password": "secret"}),
        ({"username": "petrov@ya.ru", "password": "qwerty"}),
    ],
)
async def test_login_bad(login, ivanov, credentials):
    response = await login(**credentials)
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_logout(logout, ivanov, ivanov_login, refresh_tokens):
    tokens = await ivanov_login()

    response = await logout(tokens["access_token"])
    assert response["status"] == HTTPStatus.NO_CONTENT

    # Проверка, что access-токен отозван
    response = await logout(tokens["access_token"])
    assert response["status"] == HTTPStatus.UNAUTHORIZED

    # Проверка, что refresh-токен отозван
    response = await refresh_tokens(tokens["refresh_token"])
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_refresh_tokens(refresh_tokens, ivanov, ivanov_login, check_access):
    tokens1 = await ivanov_login()

    response = await refresh_tokens(tokens1["refresh_token"])
    assert response["status"] == HTTPStatus.OK
    tokens2 = response["body"]

    # Проверка, что старый access-токен отозван
    response = await check_access(tokens1["access_token"])
    assert response["status"] == HTTPStatus.UNAUTHORIZED
    # Проверка, что новый access-токен работает
    response = await check_access(tokens2["access_token"])
    assert response["status"] == HTTPStatus.NO_CONTENT
    # Проверка, что новый refresh-токен работает
    response = await refresh_tokens(tokens2["refresh_token"])
    assert response["status"] == HTTPStatus.OK
    tokens3 = response["body"]

    # Попытка повтроного использования старого refresh-токена
    # приводит к завершению сессии и инвалидирует токены.
    response = await refresh_tokens(tokens1["refresh_token"])
    assert response["status"] == HTTPStatus.UNAUTHORIZED
    response = await check_access(tokens3["access_token"])
    assert response["status"] == HTTPStatus.UNAUTHORIZED
    response = await refresh_tokens(tokens3["refresh_token"])
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_check_access_no_token(ivanov, make_request):
    response = await make_request(hdrs.METH_GET, "/api/v1/check_access")
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_check_access_role(ivanov, ivanov_login, make_request):
    access_token = (await ivanov_login())["access_token"]

    response = await make_request(
        hdrs.METH_GET,
        "/api/v1/check_access",
        params={"allow_roles": ["admin"]},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response["status"] == HTTPStatus.FORBIDDEN
