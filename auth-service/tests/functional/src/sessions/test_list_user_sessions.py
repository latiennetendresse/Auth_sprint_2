from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


async def test_filters(list_user_sessions, ivanov, ivanov_login, logout):
    tokens = [(await ivanov_login())["access_token"] for _ in range(3)]
    await logout(tokens[1])

    for params, expected_len in [
        ({}, 3),
        ({"active": "true"}, 2),
        ({"active": "false"}, 1),
    ]:
        response = await list_user_sessions(tokens[0], params)
        assert response["status"] == HTTPStatus.OK
        assert len(response["body"]) == expected_len


async def test_pagination(list_user_sessions, ivanov, ivanov_login):
    for _ in range(3):
        token = (await ivanov_login())["access_token"]

    for params, expected_len in [
        ({}, 3),
        ({"page_size": 2, "page_number": 1}, 2),
        ({"page_size": 2, "page_number": 2}, 1),
        ({"page_size": 2, "page_number": 3}, 0),
    ]:
        response = await list_user_sessions(token, params)
        assert response["status"] == HTTPStatus.OK
        assert len(response["body"]) == expected_len


async def test_unauthorized(list_user_sessions):
    response = await list_user_sessions()
    assert response["status"] == HTTPStatus.UNAUTHORIZED
