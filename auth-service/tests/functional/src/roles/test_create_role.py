from http import HTTPStatus

import pytest
from aiohttp import hdrs

pytestmark = pytest.mark.asyncio


async def test_create(
    create_role, list_roles, ivanov, admin_role, add_role, ivanov_login
):
    await add_role(ivanov["id"], admin_role["id"])
    access_token = (await ivanov_login())["access_token"]
    response = await create_role(access_token, "subscriber")
    assert response["status"] == HTTPStatus.OK
    assert response["body"].pop("id", None)
    assert response["body"] == {"name": "subscriber"}

    response = await list_roles(access_token)
    assert response["status"] == HTTPStatus.OK
    assert len(response["body"]) == 2


async def test_unauthorized(make_request):
    response = await make_request(
        hdrs.METH_POST, "/api/v1/roles", json={"name": "subsciber"}
    )
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_forbidden(create_role, ivanov, ivanov_login):
    access_token = (await ivanov_login())["access_token"]
    response = await create_role(access_token, "subscriber")
    assert response["status"] == HTTPStatus.FORBIDDEN
