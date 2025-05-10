from .interfaces import IMusicFileRepository
from dto.music import MusicFileStats, Artist, Track, Album, AlbumID, ArtistID
from exceptions.music import MusicFileNotFoundException, ImageFileNotFoundException

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

    @staticmethod
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

    @staticmethod
    def _get_track_path(track: Track):
        return f"{track.artist_id}/{track.id}"

    @staticmethod
    def _get_artist_path(artist: Artist | ArtistID):
        return f"artists/{artist.id}"

    @staticmethod
    def _get_album_path(album: Album | AlbumID):
        return f"albums/{album.id}"

    async def save_track(
        self,
        track: Track,
        file_data: bytes,
        content_type: str,
    ) -> None:
        data_obj = BytesIO(file_data)
        await self.minio_client.put_object(
            bucket_name=self.track_bucket,
            object_name=self._get_track_path(track),
            data=data_obj,
            length=len(file_data),
            content_type=content_type,
        )

    async def save_image(
        self,
        image: Album | AlbumID | Artist | ArtistID,
        file_data: bytes,
        content_type: str,
    ) -> None:
        if isinstance(image, (Album, AlbumID)):
            name = self._get_album_path(image)
        else:
            name = self._get_artist_path(image)
        data_obj = BytesIO(file_data)
        await self.minio_client.put_object(
            bucket_name=self.image_bucket,
            object_name=name,
            data=data_obj,
            length=len(file_data),
            content_type=content_type,
        )

    async def stream_track(
        self,
        track: Track,
        start: int,
        end: int,  # TODO content type
    ) -> AsyncIterator[bytes]:
        content_length = end - start + 1
        async with ClientSession() as session:
            response = await self.minio_client.get_object(
                bucket_name=self.track_bucket,
                object_name=self._get_track_path(track),
                session=session,
                offset=start,
                length=content_length,
            )
            try:
                async for chunk in response.content.iter_chunked(8192):
                    yield chunk
            finally:
                await response.release()

    async def get_image(self, image: Album | AlbumID | Artist | ArtistID) -> bytes:
        if isinstance(image, (Album, AlbumID)):
            name = self._get_album_path(image)
        else:
            name = self._get_artist_path(image)  # TODO content type
        async with ClientSession() as session:
            try:
                response = await self.minio_client.get_object(
                    bucket_name=self.image_bucket,
                    object_name=name,
                    session=session,
                )

                data = await response.read()
                await response.release()
                return data

            except S3Error as e:
                if getattr(e, "code", None) == "NoSuchKey":
                    raise ImageFileNotFoundException(f"Image '{image.id}' not found")
                raise

    async def get_track_stats(self, track: Track):  # TODO content type
        try:
            stat = await self.minio_client.stat_object(
                self.track_bucket, self._get_track_path(track)
            )
            return MusicFileStats(size=stat.size)
        except S3Error as e:
            if getattr(e, "code", None) == "NoSuchKey":
                raise MusicFileNotFoundException(f"Music file '{track.id}' not found")
            raise

    async def delete_track(self, track: Track) -> None:
        try:
            await self.minio_client.stat_object(
                self.track_bucket, self._get_track_path(track)
            )
            await self.minio_client.remove_object(
                self.track_bucket, self._get_track_path(track)
            )
        except S3Error as e:
            if getattr(e, "code", None) == "NoSuchKey":
                raise MusicFileNotFoundException(
                    f"Music file '{track.id}' not found for delete"
                )
            raise

    async def delete_image(self, image: Album | AlbumID | Artist | ArtistID) -> None:
        if isinstance(image, (Album, AlbumID)):
            name = self._get_album_path(image)
        else:
            name = self._get_artist_path(image)
        try:
            await self.minio_client.stat_object(self.image_bucket, name)
            await self.minio_client.remove_object(self.image_bucket, name)
        except S3Error as e:
            if getattr(e, "code", None) == "NoSuchKey":
                raise ImageFileNotFoundException(
                    f"Image file '{image.id}' not found for delete"
                )
            raise
