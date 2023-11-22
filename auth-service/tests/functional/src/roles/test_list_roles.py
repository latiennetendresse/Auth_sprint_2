from http import HTTPStatus

import pytest
from aiohttp import hdrs

pytestmark = pytest.mark.asyncio


async def test_list(list_roles, ivanov, admin_role, add_role, ivanov_login):
    await add_role(ivanov["id"], admin_role["id"])
    access_token = (await ivanov_login())["access_token"]
    response = await list_roles(access_token)
    assert response["status"] == HTTPStatus.OK
    assert response["body"] == [admin_role]


async def test_unauthorized(make_request):
    response = await make_request(hdrs.METH_GET, "/api/v1/roles")
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_forbidden(list_roles, ivanov, ivanov_login):
    access_token = (await ivanov_login())["access_token"]
    response = await list_roles(access_token)
    assert response["status"] == HTTPStatus.FORBIDDEN
