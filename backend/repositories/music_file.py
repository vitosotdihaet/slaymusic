from .interfaces import IMusicFileRepository
from dto.music import MusicFileStats
from exceptions.music import MusicFileNotFoundException

from aiohttp import ClientSession
from typing import AsyncIterator
from miniopy_async import Minio, S3Error
from io import BytesIO


class MinioMusicFileRepository(IMusicFileRepository):
    def __init__(
        self,
        minio_client: Minio,
        track_bucket: str,
        image_bucket: str,
    ):
        self.minio_client = minio_client
        self.track_bucket = track_bucket
        self.image_bucket = image_bucket

    async def create(
        endpoint: str,
        access_key: str,
        secret_key: str,
        track_bucket: str,
        image_bucket: str,
    ) -> "MinioMusicFileRepository":
        client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=False
        )
        if not await client.bucket_exists(track_bucket):
            await client.make_bucket(track_bucket)
        if not await client.bucket_exists(image_bucket):
            await client.make_bucket(image_bucket)
        return MinioMusicFileRepository(client, track_bucket, image_bucket)

    async def save_image(
        self, object_name: str, file_data: bytes, content_type: str
    ) -> None:
        data_obj = BytesIO(file_data)
        await self.minio_client.put_object(
            bucket_name=self.track_bucket,
            object_name=object_name,
            data=data_obj,
            length=len(file_data),
            content_type=content_type,
        )

    async def save_cover(
        self, object_name: str, file_data: bytes, content_type: str
    ) -> None:
        data_obj = BytesIO(file_data)
        await self.minio_client.put_object(
            bucket_name=self.image_bucket,
            object_name=object_name,
            data=data_obj,
            length=len(file_data),
            content_type=content_type,
        )

    async def stream_music(
        self, music_name: str, start: int, end: int
    ) -> AsyncIterator[bytes]:
        content_length = end - start + 1
        async with ClientSession() as session:
            response = await self.minio_client.get_object(
                bucket_name=self.track_bucket,
                object_name=music_name,
                session=session,
                offset=start,
                length=content_length,
            )
            try:
                async for chunk in response.content.iter_chunked(8192):
                    yield chunk
            finally:
                await response.release()

    async def get_image(self, image_name: str) -> bytes:
        try:
            response = await self.minio_client.get_object(
                bucket_name=self.image_bucket,
                object_name=image_name,
            )

            data = await response.read()
            await response.release()
            return data

        except S3Error as e:
            if getattr(e, "code", None) == "NoSuchKey":
                raise MusicFileNotFoundException(
                    f"Image '{image_name}' not found in bucket '{self.image_bucket}'"
                )
            raise

    async def get_music_stats(self, music_name):
        try:
            stat = await self.minio_client.stat_object(self.track_bucket, music_name)
            return MusicFileStats(size=stat.size)
        except S3Error as e:
            if getattr(e, "code", None) == "NoSuchKey":
                raise MusicFileNotFoundException(
                    f"Music file '{music_name}' not found in bucket 'music'"
                )
            raise

    async def delete_file(self, object_name: str) -> None:
        try:
            await self.minio_client.stat_object(self.track_bucket, object_name)
            await self.minio_client.remove_object(self.track_bucket, object_name)
        except S3Error as e:
            if getattr(e, "code", None) == "NoSuchKey":
                raise MusicFileNotFoundException(
                    f"Music file '{object_name}' not found for delete"
                )
            raise
