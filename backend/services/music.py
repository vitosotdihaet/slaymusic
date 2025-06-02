from repositories.interfaces import (
    IMusicFileRepository,
    IAlbumRepository,
    ITrackRepository,
    IGenreRepository,
)
from dto.music import (
    TrackStream,
    Track,
    Album,
    NewAlbum,
    NewTrack,
    NewSingle,
    AlbumID,
    TrackID,
    NewGenre,
    Genre,
    GenreID,
    GenreSearchParams,
    AlbumSearchParams,
    TrackSearchParams,
    UpdateAlbum,
    UpdateTrack,
    UpdateGenre,
)
from exceptions.music import (
    InvalidStartException,
    ImageFileNotFoundException,
    AlbumNotFoundException,
)


class MusicService:
    music_file_repository: IMusicFileRepository
    track_repository: ITrackRepository
    album_repository: IAlbumRepository
    genre_repository: IGenreRepository

    def __init__(
        self,
        music_file_repository: IMusicFileRepository,
        track_repository: ITrackRepository,
        album_repository: IAlbumRepository,
        genre_repository: IGenreRepository,
    ) -> None:
        self.music_file_repository = music_file_repository
        self.track_repository = track_repository
        self.album_repository = album_repository
        self.genre_repository = genre_repository

    # Track
    async def create_track_single(
        self,
        new_track: NewSingle,
        track_data: bytes,
        track_content_type: str,
        image_data: bytes | None,
        image_content_type: str | None,
    ) -> Track:
        album = await self.album_repository.create_album(
            NewAlbum.model_validate(new_track.model_dump())
        )
        track = await self.track_repository.create_track(
            NewTrack.model_validate({**new_track.model_dump(), "album_id": album.id})
        )

        await self.music_file_repository.save_track(
            track, track_data, track_content_type
        )
        if image_content_type:
            await self.music_file_repository.save_image(
                album, image_data, image_content_type
            )
        return track

    async def create_track_to_album(
        self,
        new_track: NewTrack,
        track_data: bytes,
        track_content_type: str,
    ) -> Track:
        track = await self.track_repository.create_track(new_track)
        await self.music_file_repository.save_track(
            track, track_data, track_content_type
        )
        return track

    async def stream_track(
        self, track_id: TrackID, start: int | None = None, end: int | None = None
    ) -> TrackStream:
        track = await self.track_repository.get_track_by_id(track_id)
        stats = await self.music_file_repository.get_track_stats(track)

        file_byte_size = stats.size

        start = start if start else 0
        end = end if end else file_byte_size - 1

        if start >= file_byte_size:
            raise InvalidStartException()

        end = min(end, file_byte_size - 1, start + 1024*1024)
        content_length = end - start + 1

        stream = self.music_file_repository.stream_track(track, start, end)

        return TrackStream(stream, start, end, file_byte_size, content_length)

    async def get_track(self, track_id: TrackID) -> Track:
        return await self.track_repository.get_track_by_id(track_id)

    async def get_tracks(self, params: TrackSearchParams) -> list[Track]:
        return await self.track_repository.get_tracks(params)

    async def get_track_image(self, track_id: TrackID) -> bytes:
        track = await self.track_repository.get_track_by_id(track_id)
        return await self.music_file_repository.get_image(AlbumID(id=track.album_id))

    async def update_track(self, track: UpdateTrack) -> Track:
        return await self.track_repository.update_track(track)

    async def update_track_image(
        self, track_id: TrackID, image_data: bytes, image_content_type: str
    ):
        track = await self.track_repository.get_track_by_id(track_id)
        await self.music_file_repository.save_image(
            AlbumID(id=track.album_id), image_data, image_content_type
        )

    async def update_track_file(
        self, track_id: TrackID, track_data: bytes, track_content_type: str
    ):
        track = await self.track_repository.get_track_by_id(track_id)
        await self.music_file_repository.save_track(
            track, track_data, track_content_type
        )

    async def delete_track(self, track_id: TrackID) -> None:
        track = await self.track_repository.get_track_by_id(track_id)
        await self.music_file_repository.delete_track(track)
        tracks = await self.get_tracks(TrackSearchParams(album_id=track.album_id))
        if len(tracks) == 1:
            try:
                await self.music_file_repository.delete_image(
                    AlbumID(id=track.album_id)
                )
            except ImageFileNotFoundException:
                pass
        await self.track_repository.delete_track(track_id)

    async def delete_track_image(self, track_id: TrackID) -> None:
        track = await self.track_repository.get_track_by_id(track_id)
        await self.music_file_repository.delete_image(AlbumID(id=track.album_id))

    # Album
    async def create_album(
        self,
        new_album: NewAlbum,
        image_data: bytes | None,
        image_content_type: str | None,
    ) -> Album:
        album = await self.album_repository.create_album(new_album)
        if image_content_type:
            await self.music_file_repository.save_image(
                album, image_data, image_content_type
            )
        return album

    async def get_album(self, album_id: AlbumID) -> Album:
        return await self.album_repository.get_album_by_id(album_id)

    async def get_albums(self, params: AlbumSearchParams) -> list[Album]:
        return await self.album_repository.get_albums(params)

    async def get_album_image(self, album_id: AlbumID) -> bytes:
        await self.album_repository.get_album_by_id(album_id)
        return await self.music_file_repository.get_image(album_id)

    async def update_album(self, album: UpdateAlbum) -> Album:
        return await self.album_repository.update_album(album)

    async def update_album_image(
        self,
        album_id: AlbumID,
        image_data: bytes,
        image_content_type: str,
    ) -> None:
        await self.album_repository.get_album_by_id(album_id)
        await self.music_file_repository.save_image(
            album_id, image_data, image_content_type
        )

    async def delete_album(self, album_id: AlbumID) -> None:
        tracks = await self.get_tracks(
            TrackSearchParams(album_id=album_id.id, limit=10000)
        )
        for track in tracks:
            await self.delete_track(track)
        try:
            await self.music_file_repository.delete_image(album_id)
        except ImageFileNotFoundException:
            pass
        try:
            await self.album_repository.delete_album(album_id)
        except AlbumNotFoundException:
            pass

    async def delete_album_image(self, album_id: AlbumID) -> None:
        await self.album_repository.get_album_by_id(album_id)
        await self.music_file_repository.delete_image(album_id)

    # Genre
    async def create_genre(
        self,
        new_genre: NewGenre,
    ) -> Genre:
        return await self.genre_repository.create_genre(new_genre)

    async def get_genre(self, genre_id: GenreID) -> Genre:
        return await self.genre_repository.get_genre_by_id(genre_id)

    async def get_genres(self, params: GenreSearchParams) -> list[Genre]:
        return await self.genre_repository.get_genres(params)

    async def update_genre(self, genre: UpdateGenre) -> Genre:
        return await self.genre_repository.update_genre(genre)

    async def delete_genre(self, genre_id: GenreID) -> None:
        await self.genre_repository.delete_genre(genre_id)
