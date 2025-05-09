from repositories.interfaces import (
    IMusicFileRepository,
    IMusicMetadataRepository,
)
from dto.music import MusicStream, Track, Artist, Album, NewAlbum, NewArtist, NewTrack
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

    def _get_track_path(track: Track):
        return f"{track.artist_id}/{track.id}"

    def _get_artist_path(artist: Artist):
        return f"artist/{artist.id}"

    def _get_album_path(album: Album):
        return f"album/{album.id}"

    # Music (track + metadata)
    async def create_music_single(
        self,
        music: NewAlbum,
        music_data: bytes,
        image_data: bytes | None,
        music_content_type: str,
        image_content_type: str | None,
    ) -> None:
        album = await self.music_metadata_repository.create_album(music)
        track = await self.music_metadata_repository.create_track(
            NewTrack(music, album.id)
        )

        await self.music_file_repository.save_music(
            self._get_track_path(track), music_data, music_content_type
        )
        if image_content_type:
            await self.music_file_repository.save_image(
                self._get_album_path(album), image_data, image_content_type
            )

    async def create_music_to_album(
        self,
        music: NewTrack,
        music_data: bytes,
        music_content_type: str,
    ) -> None:
        track = await self.music_metadata_repository.add(music)
        await self.music_file_repository.save_music(
            self._get_track_path(track), music_data, music_content_type
        )

    async def stream_music(
        self, track: Track, start: int | None = None, end: int | None = None
    ) -> MusicStream:
        stats = await self.music_file_repository.get_music_stats(
            self._get_track_path(track)
        )

        file_byte_size = stats.size

        start = start if start else 0
        end = end if end else file_byte_size - 1

        if start >= file_byte_size:
            raise InvalidStartException()

        end = min(end, file_byte_size - 1)
        content_length = end - start + 1

        stream = self.music_file_repository.stream_music(
            self._get_track_path(track), start, end
        )

        return MusicStream(stream, start, end, file_byte_size, content_length)

    async def get_music_metadata(self, id: int) -> Track:
        return await self.music_metadata_repository.get_track_by_id(id)

    async def get_musics_metadata_by_album(
        self, id: int, skip: int, limit: int
    ) -> list[Track]:
        return await self.music_metadata_repository.get_tracks_by_album(id, skip, limit)

    async def get_musics_metadata_by_artist(
        self, id: int, skip: int, limit: int
    ) -> list[Track]:
        return await self.music_metadata_repository.get_tracks_by_artist(
            id, skip, limit
        )

    async def get_musics_metadata(self, skip: int, limit: int) -> list[Track]:
        return await self.music_metadata_repository.get_tracks(skip, limit)

    async def update_music_metadata(self, track: Track) -> Track:
        return await self.music_metadata_repository.update_track(id, track)

    async def update_music_file(
        self, track: Track, music_data: bytes, music_content_type: str
    ):
        await self.music_file_repository.save_music(
            self._get_track_path(track), music_data, music_content_type
        )

    async def delete_music(self, track: Track) -> None:
        await self.music_file_repository.delete_file(self._get_track_path(track))
        await self.music_metadata_repository.delete_track(track.id)

    # Album
    async def create_album(
        self,
        new_album: NewAlbum,
        image_data: bytes,
        image_content_type: str,
    ) -> Album:
        album = await self.music_metadata_repository.create_album(new_album)
        await self.music_file_repository.save_image(
            self._get_album_path(album), image_data, image_content_type
        )
        return album

    async def get_album(self, id: int) -> Album:
        return await self.music_metadata_repository.get_album_by_id(id)

    async def get_album_image(self, album: Album) -> bytes:
        return await self.music_file_repository.get_image(self._get_album_path(album))

    async def update_album(self, id: int, album: NewAlbum) -> Album:
        return await self.music_metadata_repository.update_album(id, Album)

    async def update_album_image(
        self,
        album: Album,
        image_data: bytes,
        image_content_type: str,
    ) -> Album:
        await self.music_file_repository.save_image(
            self._get_album_path(album), image_data, image_content_type
        )

    async def delete_album(self, album: Album) -> None:
        await self.music_file_repository.delete_file(self._get_album_path(album))
        await self.music_metadata_repository.delete_album(album.id)

    # Artist
    async def create_artist(
        self,
        new_artist: NewArtist,
        image_data: bytes | None,
        image_content_type: str | None,
    ) -> Artist:
        artist = await self.music_metadata_repository.create_artist(new_artist)
        if image_content_type:
            await self.music_file_repository.save_image(
                self._get_artist_path(artist), image_data, image_content_type
            )
        return artist

    async def get_artist(self, id: int) -> Artist:
        return await self.music_metadata_repository.get_artist_by_id(id)

    async def get_artist_image(self, artist: Artist) -> bytes:
        return await self.music_file_repository.get_image(self._get_artist_path(artist))

    async def update_artist(self, id: int, artist: NewArtist) -> Artist:
        return await self.music_metadata_repository.update_artist(id, artist)

    async def update_artist_image(
        self,
        artist: Artist,
        image_data: bytes,
        image_content_type: str,
    ):
        await self.music_file_repository.save_image(
            self._get_artist_path(artist), image_data, image_content_type
        )

    async def delete_artist(self, artist: Artist) -> None:
        await self.music_file_repository.delete_file(self._get_artist_path(artist))
        await self.music_metadata_repository.delete_artist(artist.id)
