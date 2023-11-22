from http import HTTPStatus
from uuid import uuid4

import pytest
from aiohttp import hdrs

pytestmark = pytest.mark.asyncio


async def test_delete(
    delete_user_role,
    ivanov,
    admin_role,
    add_role,
    ivanov_login,
    list_roles,
    refresh_tokens,
):
    await add_role(ivanov["id"], admin_role["id"])
    ivanov_tokens = await ivanov_login()

    response = await list_roles(ivanov_tokens["access_token"])
    assert response["status"] == HTTPStatus.OK

    response = await delete_user_role(
        ivanov_tokens["access_token"], ivanov["id"], admin_role["id"]
    )
    assert response["status"] == HTTPStatus.NO_CONTENT

    # По статусу понимаем, что токен отозван и надо обновить
    response = await list_roles(ivanov_tokens["access_token"])
    assert response["status"] == HTTPStatus.UNAUTHORIZED

    response = await refresh_tokens(ivanov_tokens["refresh_token"])
    ivanov_tokens = response["body"]

    response = await list_roles(ivanov_tokens["access_token"])
    assert response["status"] == HTTPStatus.FORBIDDEN


async def test_unauthorized(make_request, ivanov, admin_role):
    response = await make_request(
        hdrs.METH_DELETE,
        f"/api/v1/users/{ivanov['id']}/roles",
        json={"role_id": admin_role["id"]},
    )
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_forbidden(delete_user_role, ivanov, ivanov_login, admin_role):
    access_token = (await ivanov_login())["access_token"]
    response = await delete_user_role(access_token, ivanov["id"], admin_role["id"])
    assert response["status"] == HTTPStatus.FORBIDDEN


async def test_not_found(delete_user_role, admin_role, ivanov, add_role, ivanov_login):
    await add_role(ivanov["id"], admin_role["id"])
    access_token = (await ivanov_login())["access_token"]
    response = await delete_user_role(access_token, str(uuid4()), str(uuid4()))
    assert response["status"] == HTTPStatus.NOT_FOUND
