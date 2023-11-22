from typing import Optional

from httpx import AsyncClient

client: Optional[AsyncClient] = None


async def get_http_client() -> AsyncClient:
    return client
