import os
from dotenv import load_dotenv
from httpx import AsyncClient
import pytest_asyncio

assert load_dotenv(".env", override=True)


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        base_url=f"http://localhost:{os.getenv('BACKEND_PORT', default='8000')}"
    ) as client:
        yield client
