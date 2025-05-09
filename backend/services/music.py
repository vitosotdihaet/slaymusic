from repositories.interfaces import (
    IMusicFileRepository,
    IMusicMetadataRepository,
)
from dto.music import MusicStream, Track, Artist
from exceptions.music import InvalidStartException


class MusicService:
    music_file_repository: IMusicFileRepository
    music_metadata_repository: IMusicMetadataRepository

    def __init__(
        self,
        music_file_repository: IMusicFileRepository,
        music_metadata_repository: IMusicMetadataRepository,
    ) -> None:
        self.music_file_repository = music_file_repository
        self.music_metadata_repository = music_metadata_repository

    async def stream_music(
        self, music_name: str, start: int | None = None, end: int | None = None
    ) -> MusicStream:
        stats = await self.music_file_repository.get_music_stats(music_name)

        file_byte_size = stats.size

        start = start if start else 0
        end = end if end else file_byte_size - 1

        if start >= file_byte_size:
            raise InvalidStartException()

        end = min(end, file_byte_size - 1)
        content_length = end - start + 1

        stream = self.music_file_repository.stream_music(music_name, start, end)

        return MusicStream(stream, start, end, file_byte_size, content_length)

    async def create_music(
        self, track: Track, file_data: bytes, content_type: str
    ) -> None:
        await self.music_file_repository.save_music(track.name, file_data, content_type)
        await self.music_metadata_repository.add(track)

    async def create_cover(
        self, track: Track, file_data: bytes, content_type: str
    ) -> None:
        await self.music_file_repository.save_cover(
            track.cover_file_path, file_data, content_type
        )

    async def get_metadata(self, name: str) -> Track:
        meta = await self.music_metadata_repository.get(name)
        return meta

    # async def create_artist(self, artist: Artist):
    #     await self.artist_repository.add(artist)

    async def update_metadata(self, name: str, track: Track) -> None:
        await self.music_metadata_repository.get(name)
        await self.music_metadata_repository.update(name, track)

    async def delete_music(self, name: str) -> None:
        await self.music_metadata_repository.delete(name)
        await self.music_file_repository.delete_file(name)
