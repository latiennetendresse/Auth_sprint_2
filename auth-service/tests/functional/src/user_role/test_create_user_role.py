from http import HTTPStatus
from uuid import uuid4

import pytest
from aiohttp import hdrs

pytestmark = pytest.mark.asyncio


async def test_create(
    create_user_role,
    ivanov,
    ivanov_login,
    petrov,
    petrov_login,
    admin_role,
    add_role,
    list_roles,
    refresh_tokens,
):
    petrov_tokens1 = await petrov_login()
    response = await list_roles(petrov_tokens1["access_token"])
    assert response["status"] == HTTPStatus.FORBIDDEN

    await add_role(ivanov["id"], admin_role["id"])
    ivanov_tokens = await ivanov_login()
    response = await create_user_role(
        ivanov_tokens["access_token"], petrov["id"], admin_role["id"]
    )
    assert response["status"] == HTTPStatus.NO_CONTENT

    # По статусу понимаем, что токен отозван и надо обновить
    response = await list_roles(petrov_tokens1["access_token"])
    assert response["status"] == HTTPStatus.UNAUTHORIZED

    response = await refresh_tokens(petrov_tokens1["refresh_token"])
    petrov_tokens2 = response["body"]
    response = await list_roles(petrov_tokens2["access_token"])
    assert response["status"] == HTTPStatus.OK


async def test_unauthorized(make_request, ivanov, admin_role):
    response = await make_request(
        hdrs.METH_POST,
        f"/api/v1/users/{ivanov['id']}/roles",
        json={"role_id": admin_role["id"]},
    )
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_forbidden(create_user_role, ivanov, ivanov_login, admin_role):
    access_token = (await ivanov_login())["access_token"]
    response = await create_user_role(access_token, ivanov["id"], admin_role["id"])
    assert response["status"] == HTTPStatus.FORBIDDEN


async def test_user_not_found(
    create_user_role, ivanov, ivanov_login, admin_role, add_role
):
    await add_role(ivanov["id"], admin_role["id"])
    ivanov_token = (await ivanov_login())["access_token"]
    response = await create_user_role(ivanov_token, str(uuid4()), admin_role["id"])
    assert response["status"] == HTTPStatus.BAD_REQUEST


async def test_role_not_found(
    create_user_role, ivanov, ivanov_login, admin_role, add_role, petrov
):
    await add_role(ivanov["id"], admin_role["id"])
    ivanov_token = (await ivanov_login())["access_token"]
    response = await create_user_role(ivanov_token, petrov["id"], str(uuid4()))
    assert response["status"] == HTTPStatus.BAD_REQUEST


async def test_user_role_exists(
    create_user_role, ivanov, ivanov_login, admin_role, add_role
):
    await add_role(ivanov["id"], admin_role["id"])
    ivanov_token = (await ivanov_login())["access_token"]
    response = await create_user_role(ivanov_token, ivanov["id"], admin_role["id"])
    assert response["status"] == HTTPStatus.BAD_REQUEST
