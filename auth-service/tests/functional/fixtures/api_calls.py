import pytest
from aiohttp import hdrs


@pytest.fixture
async def register(make_request):
    async def inner(json: dict) -> dict:
        return await make_request(hdrs.METH_POST, "/api/v1/register", json=json)

    return inner


@pytest.fixture
async def login(make_request):
    async def inner(username: str, password: str) -> dict:
        return await make_request(
            hdrs.METH_POST,
            "/api/v1/login",
            json={"username": username, "password": password},
        )

    return inner


@pytest.fixture
async def logout(make_request):
    async def inner(access_token: str) -> dict:
        return await make_request(
            hdrs.METH_POST,
            "/api/v1/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return inner


@pytest.fixture
async def refresh_tokens(make_request):
    async def inner(refresh_token: str) -> dict:
        return await make_request(
            hdrs.METH_POST,
            "/api/v1/refresh_tokens",
            json={"refresh_token": refresh_token},
        )

    return inner


@pytest.fixture
async def check_access(make_request):
    async def inner(access_token: str) -> int:
        return await make_request(
            hdrs.METH_GET,
            "/api/v1/check_access",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return inner


@pytest.fixture
async def list_user_sessions(make_request):
    async def inner(token: str = None, params: dict = {}) -> dict:
        return await make_request(
            hdrs.METH_GET,
            "/api/v1/user/sessions",
            params=params,
            headers={"Authorization": f"Bearer {token}"} if token else {},
        )

    return inner


@pytest.fixture
async def end_user_session(make_request):
    async def inner(session_id: str, token: str = None) -> dict:
        return await make_request(
            hdrs.METH_DELETE,
            f"/api/v1/user/sessions/{session_id}",
            headers={"Authorization": f"Bearer {token}"} if token else {},
        )

    return inner


@pytest.fixture
async def list_roles(make_request):
    async def inner(access_token: str) -> dict:
        return await make_request(
            hdrs.METH_GET,
            "/api/v1/roles",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return inner


@pytest.fixture
async def create_role(make_request):
    async def inner(access_token: str, role_name: str) -> dict:
        return await make_request(
            hdrs.METH_POST,
            "/api/v1/roles",
            json={"name": role_name},
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return inner


@pytest.fixture
async def delete_role(make_request):
    async def inner(access_token: str, role_id: str) -> dict:
        return await make_request(
            hdrs.METH_DELETE,
            f"/api/v1/roles/{role_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return inner


@pytest.fixture
async def patch_role(make_request):
    async def inner(access_token: str, role_id: str, new_name: str) -> dict:
        return await make_request(
            hdrs.METH_PATCH,
            f"/api/v1/roles/{role_id}",
            json={"name": new_name},
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return inner


@pytest.fixture
async def create_user_role(make_request):
    async def inner(access_token: str, user_id: str, role_id: str) -> dict:
        return await make_request(
            hdrs.METH_POST,
            f"/api/v1/users/{user_id}/roles",
            json={"role_id": role_id},
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return inner


@pytest.fixture
async def delete_user_role(make_request):
    async def inner(access_token: str, user_id: str, role_id: str) -> dict:
        return await make_request(
            hdrs.METH_DELETE,
            f"/api/v1/users/{user_id}/roles",
            json={"role_id": role_id},
            headers={"Authorization": f"Bearer {access_token}"},
        )

    return inner
