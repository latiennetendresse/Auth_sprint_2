import asyncio

import pytest
from aiohttp import ClientSession

from settings import settings


@pytest.fixture(scope="session")
def event_loop(request):
    """Создавать новый event loop для каждого теста."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def aiohttp_session():
    session = ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_request(aiohttp_session: ClientSession):
    async def inner(
        method: str,
        endpoint: str,
        params: dict = {},
        json: dict = {},
        headers: dict = {},
    ):
        url = f"{settings.api_url}{endpoint}"
        async with aiohttp_session.request(
            method, url, params=params, json=json, headers=headers
        ) as response:
            return {
                "status": response.status,
                "headers": response.headers,
                "body": await response.json(),
            }

    return inner
