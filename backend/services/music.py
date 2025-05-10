from repositories.interfaces import (
    IMusicFileRepository,
    IArtistRepository,
    IAlbumRepository,
    ITrackRepository,
)
from dto.music import (
    MusicStream,
    Track,
    Artist,
    Album,
    NewAlbum,
    NewArtist,
    NewTrack,
    NewSingle,
    AlbumID,
    ArtistID,
    TrackID,
)
from exceptions.music import (
    InvalidStartException,
    ImageFileNotFoundException,
)


class MusicService:
    music_file_repository: IMusicFileRepository
    track_repository: ITrackRepository
    album_repository: IAlbumRepository
    artist_repository: IArtistRepository

    def __init__(
        self,
        music_file_repository: IMusicFileRepository,
        track_repository: ITrackRepository,
        album_repository: IAlbumRepository,
        artist_repository: IArtistRepository,
    ) -> None:
        self.music_file_repository = music_file_repository
        self.track_repository = track_repository
        self.album_repository = album_repository
        self.artist_repository = artist_repository

    # Music (track + metadata)
    async def create_music_single(
        self,
        new_track: NewSingle,
        music_data: bytes,
        music_content_type: str,
        image_data: bytes | None,
        image_content_type: str | None,
    ) -> Track:
        album = await self.album_repository.create_album(
            NewAlbum(name=new_track.name, artist_id=new_track.artist_id)
        )
        track = await self.track_repository.create_track(
            NewTrack(
                name=new_track.name, artist_id=new_track.artist_id, album_id=album.id
            )
        )

        await self.music_file_repository.save_track(
            track, music_data, music_content_type
        )
        if image_content_type:
            await self.music_file_repository.save_image(
                album, image_data, image_content_type
            )
        return track

    async def create_music_to_album(
        self,
        new_track: NewTrack,
        music_data: bytes,
        music_content_type: str,
    ) -> Track:
        track = await self.track_repository.create_track(new_track)
        await self.music_file_repository.save_track(
            track, music_data, music_content_type
        )
        return track

    async def stream_music(
        self, track_id: TrackID, start: int | None = None, end: int | None = None
    ) -> MusicStream:
        track = await self.track_repository.get_track_by_id(track_id)
        stats = await self.music_file_repository.get_track_stats(track)

        file_byte_size = stats.size

        start = start if start else 0
        end = end if end else file_byte_size - 1

        if start >= file_byte_size:
            raise InvalidStartException()

        end = min(end, file_byte_size - 1)
        content_length = end - start + 1

        stream = self.music_file_repository.stream_track(track, start, end)

        return MusicStream(stream, start, end, file_byte_size, content_length)

    async def get_music_metadata(self, track_id: TrackID) -> Track:
        return await self.track_repository.get_track_by_id(track_id)

    async def get_musics_metadata_by_album(
        self, album_id: AlbumID, skip: int, limit: int
    ) -> list[Track]:
        return await self.track_repository.get_tracks_by_album(album_id, skip, limit)

    async def get_musics_metadata_by_artist(
        self, artist_id: ArtistID, skip: int, limit: int
    ) -> list[Track]:
        return await self.track_repository.get_tracks_by_artist(artist_id, skip, limit)

    async def get_musics_metadata(self, skip: int, limit: int) -> list[Track]:
        return await self.track_repository.get_tracks(skip, limit)

    async def get_music_image(self, track_id: TrackID) -> bytes:
        track = await self.track_repository.get_track_by_id(track_id)
        return await self.music_file_repository.get_image(AlbumID(id=track.album_id))

    async def update_music_metadata(self, track: Track) -> Track:
        return await self.track_repository.update_track(track)

    async def update_music_file(
        self, track_id: TrackID, image_data: bytes, image_content_type: str
    ):
        track = await self.track_repository.get_track_by_id(track_id)
        await self.music_file_repository.save_image(
            AlbumID(id=track.album_id), image_data, image_content_type
        )

    async def update_music(
        self, track_id: TrackID, music_data: bytes, music_content_type: str
    ):
        track = await self.track_repository.get_track_by_id(track_id)
        await self.music_file_repository.save_track(
            track, music_data, music_content_type
        )

    async def delete_music(self, track_id: TrackID) -> None:
        track = await self.track_repository.get_track_by_id(track_id)
        await self.music_file_repository.delete_track(track)
        await self.track_repository.delete_track(track_id)

    async def delete_music_image(self, track_id: TrackID) -> None:
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

    async def get_albums_by_artist(
        self, artist_id: ArtistID, skip: int = 0, limit: int = 100
    ) -> list[Album]:
        return await self.album_repository.get_albums_by_artist(artist_id, skip, limit)

    async def get_albums(self, skip: int = 0, limit: int = 100) -> list[Album]:
        return await self.album_repository.get_albums(skip, limit)

    async def get_album_image(self, album_id: AlbumID) -> bytes:
        await self.album_repository.get_album_by_id(album_id)
        return await self.music_file_repository.get_image(album_id)

    async def update_album(self, album: Album) -> Album:
        return await self.album_repository.update_album(album)

    async def update_album_image(
        self,
        album_id: AlbumID,
        image_data: bytes,
        image_content_type: str,
    ) -> Album:
        await self.album_repository.get_album_by_id(album_id)
        await self.music_file_repository.save_image(
            album_id, image_data, image_content_type
        )

    async def delete_album(self, album_id: AlbumID) -> None:
        await self.album_repository.delete_album(album_id)
        try:
            await self.music_file_repository.delete_image(album_id)
        except ImageFileNotFoundException:
            pass

    async def delete_album_image(self, album_id: AlbumID) -> None:
        await self.album_repository.delete_album(album_id)
        await self.music_file_repository.delete_image(album_id)

    # Artist
    async def create_artist(
        self,
        new_artist: NewArtist,
        image_data: bytes | None,
        image_content_type: str | None,
    ) -> Artist:
        artist = await self.artist_repository.create_artist(new_artist)
        if image_content_type:
            await self.music_file_repository.save_image(
                artist, image_data, image_content_type
            )
        return artist

    async def get_artist(self, artist_id: ArtistID) -> Artist:
        return await self.artist_repository.get_artist_by_id(artist_id)

    async def get_artist_image(self, artist_id: ArtistID) -> bytes:
        await self.artist_repository.get_artist_by_id(artist_id)
        return await self.music_file_repository.get_image(artist_id)

    async def get_artists(self, skip: int = 0, limit: int = 100) -> list[Artist]:
        return await self.artist_repository.get_artists(skip, limit)

    async def update_artist(self, artist: Artist) -> Artist:
        return await self.artist_repository.update_artist(artist)

    async def update_artist_image(
        self,
        artist_id: ArtistID,
        image_data: bytes,
        image_content_type: str,
    ):
        await self.artist_repository.get_artist_by_id(artist_id)
        await self.music_file_repository.save_image(
            artist_id, image_data, image_content_type
        )

    async def delete_artist(self, artist_id: ArtistID) -> None:
        await self.artist_repository.delete_artist(artist_id)
        try:
            await self.music_file_repository.delete_image(artist_id)
        except ImageFileNotFoundException:
            pass

    async def delete_artist_image(self, artist_id: ArtistID) -> None:
        await self.artist_repository.get_artist_by_id(artist_id)
        await self.music_file_repository.delete_image(artist_id)
