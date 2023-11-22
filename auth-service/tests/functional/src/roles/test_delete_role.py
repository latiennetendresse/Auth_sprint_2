from http import HTTPStatus
from uuid import uuid4

import pytest
from aiohttp import hdrs

pytestmark = pytest.mark.asyncio


async def test_delete(
    delete_role, create_role, list_roles, ivanov, admin_role, add_role, ivanov_login
):
    await add_role(ivanov["id"], admin_role["id"])
    access_token = (await ivanov_login())["access_token"]

    response = await create_role(access_token, "new_role")
    new_role_id = response["body"]["id"]
    response = await list_roles(access_token)
    assert response["status"] == HTTPStatus.OK
    assert len(response["body"]) == 2

    response = await delete_role(access_token, new_role_id)
    assert response["status"] == HTTPStatus.NO_CONTENT
    response = await list_roles(access_token)
    assert response["status"] == HTTPStatus.OK
    assert len(response["body"]) == 1


async def test_unauthorized(admin_role, make_request):
    response = await make_request(hdrs.METH_DELETE, f"/api/v1/roles/{admin_role['id']}")
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_forbidden(delete_role, admin_role, ivanov, ivanov_login):
    access_token = (await ivanov_login())["access_token"]
    response = await delete_role(access_token, admin_role["id"])
    assert response["status"] == HTTPStatus.FORBIDDEN


async def test_not_found(delete_role, admin_role, ivanov, add_role, ivanov_login):
    await add_role(ivanov["id"], admin_role["id"])
    access_token = (await ivanov_login())["access_token"]
    response = await delete_role(access_token, str(uuid4()))
    assert response["status"] == HTTPStatus.NOT_FOUND
