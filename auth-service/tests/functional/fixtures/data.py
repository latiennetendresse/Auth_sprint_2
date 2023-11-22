import pytest


@pytest.fixture
async def ivanov(register) -> dict:
    user = {
        "email": "ivanov@ya.ru",
        "password": "qwerty",
        "name": "Ivan Ivanov",
    }
    response = await register(user)
    return response["body"]


@pytest.fixture
async def ivanov_login(login):
    async def inner(password: str = "qwerty") -> dict:
        response = await login("ivanov@ya.ru", password)
        return response["body"]

    return inner


@pytest.fixture
async def petrov(register) -> dict:
    user = {
        "email": "petrov@ya.ru",
        "password": "qwerty",
        "name": "Petr Petrov",
    }
    response = await register(user)
    return response["body"]


@pytest.fixture
async def petrov_login(login):
    async def inner(password: str = "qwerty") -> dict:
        response = await login("petrov@ya.ru", password)
        return response["body"]

    return inner
