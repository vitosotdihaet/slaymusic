import asyncio
from miniopy_async import Minio
import os

from configs.database import get_redis_client_generator
from configs.environment import settings


async def load_scripts(db_name: str, scripts_dir: str = "scripts/") -> None:
    async with get_redis_client_generator(db_name)() as client:
        for filename in os.listdir(scripts_dir):
            filepath = os.path.join(scripts_dir, filename)
            with open(filepath, "r") as f:
                lua_script_content = f.read()
            await client.script_load(lua_script_content)


async def setup():
    print("Setting up Minio...")
    async with Minio(
        "minio-service:" + str(settings.MINIO_PORT),
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        secure=False,
    ) as client:
        if not await client.bucket_exists(settings.MINIO_MUSIC_BUCKET):
            await client.make_bucket(settings.MINIO_MUSIC_BUCKET)
        if not await client.bucket_exists(settings.MINIO_COVER_BUCKET):
            await client.make_bucket(settings.MINIO_COVER_BUCKET)

    print("Setting up Redis...")
    await load_scripts("track-queue")


if __name__ == "__main__":
    asyncio.run(setup())
    print("Setup done!")
