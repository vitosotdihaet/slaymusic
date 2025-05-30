import asyncio
from miniopy_async import Minio

from configs.environment import settings


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


if __name__ == "__main__":
    asyncio.run(setup())
    print("Setup done!")
