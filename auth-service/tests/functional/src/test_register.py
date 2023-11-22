from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


async def test_register(register):
    user = {
        "email": "ivanov@ya.ru",
        "password": "qwerty",
        "name": "Ivan Ivanov",
    }
    response = await register(user)
    assert response["status"] == HTTPStatus.OK
    assert response["body"].pop("id", None)
    assert response["body"] == {
        "email": "ivanov@ya.ru",
        "name": "Ivan Ivanov",
    }

    response = await register(user)
    assert response["status"] == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize(
    "user",
    [
        ({"email": "ivanov", "name": "Ivan Ivanov", "password": "qwerty"}),
        ({"email": "ivanov@ya.ru", "name": "Ivan Ivanov"}),
        ({"email": "ivanov@ya.ru", "password": "qwerty"}),
        ({"name": "Ivan Ivanov", "password": "qwerty"}),
    ],
)
async def test_register_validation(register, user):
    response = await register(user)
    assert response["status"] == HTTPStatus.UNPROCESSABLE_ENTITY
