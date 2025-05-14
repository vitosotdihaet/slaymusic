import os
from httpx import AsyncClient
import pytest_asyncio


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(base_url=f"http://localhost:{os.getenv('BACKEND_PORT', default='8000')}") as client:
        yield client
