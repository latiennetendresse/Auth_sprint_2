from http import HTTPStatus

import pytest
from aiohttp import hdrs

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "user_patch,expected_response",
    [
        ({"email": "petrov@ya.ru"}, {"email": "petrov@ya.ru", "name": "Ivan Ivanov"}),
        ({"name": "Vasya Ivanov"}, {"email": "ivanov@ya.ru", "name": "Vasya Ivanov"}),
    ],
)
async def test_update_info(
    ivanov, ivanov_login, user_patch, expected_response, make_request
):
    access_token = (await ivanov_login())["access_token"]

    response = await make_request(
        hdrs.METH_PATCH,
        "/api/v1/user",
        json=user_patch,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response["status"] == HTTPStatus.OK
    assert response["body"].pop("id", None)
    assert response["body"] == expected_response

    response = await make_request(
        hdrs.METH_GET,
        "/api/v1/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response["status"] == HTTPStatus.OK
    assert response["body"].pop("id", None)
    assert response["body"] == expected_response


async def test_update_password(ivanov, ivanov_login, make_request):
    access_token = (await ivanov_login())["access_token"]

    response = await make_request(
        hdrs.METH_PATCH,
        "/api/v1/user",
        json={"password": "newpass"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response["status"] == HTTPStatus.OK
    await ivanov_login("newpass")


async def test_unauthorized(make_request):
    response = await make_request(
        hdrs.METH_PATCH,
        "/api/v1/user",
        json={"email": "petrov@ya.ru"},
    )
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_user_deleted(ivanov, ivanov_login, db_delete, make_request):
    access_token = (await ivanov_login())["access_token"]
    await db_delete("users", ivanov["id"])

    response = await make_request(
        hdrs.METH_PATCH,
        "/api/v1/user",
        json={"email": "petrov@ya.ru"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response["status"] == HTTPStatus.NOT_FOUND
