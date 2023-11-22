from http import HTTPStatus
from uuid import uuid4

import pytest

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "src, dst",
    [
        (0, 0),
        (0, 1),
    ],
)
async def test_end_user_session(
    end_user_session, list_user_sessions, src, dst, ivanov, ivanov_login
):
    tokens = [(await ivanov_login())["access_token"] for _ in range(3)]
    sessions = (await list_user_sessions(tokens[0]))["body"][::-1]

    # Завершение сессии dst из сессии src
    response = await end_user_session(sessions[dst]["id"], tokens[src])
    assert response["status"] == HTTPStatus.NO_CONTENT

    # Запрос из завершённой сессии
    response = await list_user_sessions(tokens[dst])
    assert response["status"] == HTTPStatus.UNAUTHORIZED

    # Запрос из активной сессии
    response = await list_user_sessions(tokens[1 - dst])
    assert response["status"] == HTTPStatus.OK


async def test_unauthorized(end_user_session):
    response = await end_user_session(str(uuid4()))
    assert response["status"] == HTTPStatus.UNAUTHORIZED


async def test_not_found(end_user_session, ivanov, ivanov_login):
    token = (await ivanov_login())["access_token"]
    response = await end_user_session(str(uuid4()), token)
    assert response["status"] == HTTPStatus.NOT_FOUND
