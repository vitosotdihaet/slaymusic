from .interfaces import IMusicFileRepository
from dto.music import MusicFileStats, Track, Album, AlbumID
from dto.accounts import User, UserID, Playlist, PlaylistID
from exceptions.music import MusicFileNotFoundException, ImageFileNotFoundException

from typing import AsyncIterator
from miniopy_async import Minio, S3Error
from io import BytesIO


class MinioMusicFileRepository(IMusicFileRepository):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        track_bucket: str,
        image_bucket: str,
    ):
        self.minio_client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=False
        )
        self.track_bucket = track_bucket
        self.image_bucket = image_bucket

    @staticmethod
    def _get_track_path(track: Track):
        return f"{track.artist_id}/{track.id}"

    @staticmethod
    def _get_artist_path(artist: User | UserID):
        return f"user/{artist.id}"

    @staticmethod
    def _get_album_path(album: Album | AlbumID):
        return f"albums/{album.id}"

    @staticmethod
    def _get_playlist_path(playlist: Playlist | PlaylistID):
        return f"playlist/{playlist.id}"

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
        image: Album | AlbumID | User | UserID | Playlist | PlaylistID,
        file_data: bytes,
        content_type: str,
    ) -> None:
        if isinstance(image, (Album, AlbumID)):
            name = self._get_album_path(image)
        elif isinstance(image, (User, UserID)):
            name = self._get_artist_path(image)
        else:
            name = self._get_playlist_path(image)
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
        end: int,
    ) -> AsyncIterator[bytes]:
        content_length = end - start + 1
        response = await self.minio_client.get_object(
            bucket_name=self.track_bucket,
            object_name=self._get_track_path(track),
            offset=start,
            length=content_length,
        )
        try:
            async for chunk in response.content.iter_chunked(8192):
                yield chunk
        finally:
            await response.release()

    async def get_image(
        self, image: Album | AlbumID | User | UserID | Playlist | PlaylistID
    ) -> bytes:
        if isinstance(image, (Album, AlbumID)):
            name = self._get_album_path(image)
        elif isinstance(image, (User, UserID)):
            name = self._get_artist_path(image)
        else:
            name = self._get_playlist_path(image)
        try:
            response = await self.minio_client.get_object(
                bucket_name=self.image_bucket,
                object_name=name,
            )

            data = await response.read()
            await response.release()
            return data

        except S3Error as e:
            if getattr(e, "code", None) == "NoSuchKey":
                raise ImageFileNotFoundException(f"Image '{image.id}' not found")
            raise

    async def get_track_stats(self, track: Track) -> MusicFileStats:
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

    async def delete_image(
        self, image: Album | AlbumID | User | UserID | Playlist | PlaylistID
    ) -> None:
        if isinstance(image, (Album, AlbumID)):
            name = self._get_album_path(image)
        elif isinstance(image, (User, UserID)):
            name = self._get_artist_path(image)
        else:
            name = self._get_playlist_path(image)
        try:
            await self.minio_client.stat_object(self.image_bucket, name)
            await self.minio_client.remove_object(self.image_bucket, name)
        except S3Error as e:
            if getattr(e, "code", None) == "NoSuchKey":
                raise ImageFileNotFoundException(
                    f"Image file '{image.id}' not found for delete"
                )
            raise
