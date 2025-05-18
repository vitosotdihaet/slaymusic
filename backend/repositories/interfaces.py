from dto.music import (
    MusicFileStats,
    Track,
    Artist,
    Album,
    NewAlbum,
    NewArtist,
    NewTrack,
    ArtistID,
    AlbumID,
    TrackID,
    NewGenre,
    Genre,
    GenreID,
    GenreSearchParams,
    ArtistSearchParams,
    AlbumSearchParams,
    TrackSearchParams,
)
from dto.user_activity import (
    ActiveUsers,
    TracksCompletionRate,
    UserActivity,
    MostPlayedTracks,
    UserActivityFilter,
    UserActivityPost,
)

from dto.accounts import (
    User,
    UserID,
    NewRoleUser,
    UserUsername,
    LoginUserWithID,
    NewPlaylist,
    Playlist,
    PlaylistID,
    PlaylistTrack,
    NewPlaylistTrack,
)

from typing import AsyncIterator, Protocol, Optional


class IMusicFileRepository(Protocol):
    async def save_track(
        self, track: Track, file_data: bytes, content_type: str
    ) -> None: ...

    async def save_image(
        self,
        image: Album | AlbumID | Artist | ArtistID,
        file_data: bytes,
        content_type: str,
    ) -> None: ...

    async def stream_track(
        self, track: Track, start: int, end: int
    ) -> AsyncIterator[bytes]: ...

    async def get_track_stats(self, track: Track) -> MusicFileStats: ...
    async def get_image(self, image: Album | AlbumID | Artist | ArtistID) -> bytes: ...
    async def delete_track(self, track: Track) -> None: ...
    async def delete_image(
        self, image: Album | AlbumID | Artist | ArtistID
    ) -> None: ...


class IGenreRepository(Protocol):
    async def create_genre(self, new_genre: NewGenre) -> Genre: ...
    async def get_genre_by_id(self, genre: GenreID) -> Genre: ...
    async def get_genres(self, params: GenreSearchParams) -> list[Genre]: ...
    async def update_genre(self, new_genre: Genre) -> Genre: ...
    async def delete_genre(self, genre: GenreID) -> None: ...


class IArtistRepository(Protocol):
    async def create_artist(self, new_artist: NewArtist) -> Artist: ...
    async def get_artist_by_id(self, artist: ArtistID) -> Artist: ...
    async def get_artists(self, params: ArtistSearchParams) -> list[Artist]: ...
    async def update_artist(self, new_artist: Artist) -> Artist: ...
    async def delete_artist(self, artist: ArtistID) -> None: ...


class IAlbumRepository(Protocol):
    async def create_album(self, new_album: NewAlbum) -> Album: ...
    async def get_album_by_id(self, album: AlbumID) -> Album: ...
    async def get_albums(self, params: AlbumSearchParams) -> list[Album]: ...
    async def update_album(self, new_album: Album) -> Album: ...
    async def delete_album(self, album: AlbumID) -> None: ...


class ITrackRepository(Protocol):
    async def create_track(self, new_track: NewTrack) -> Track: ...
    async def get_track_by_id(self, track: TrackID) -> Track: ...
    async def get_tracks(self, params: TrackSearchParams) -> list[Track]: ...
    async def update_track(self, new_track: Track) -> Track: ...
    async def delete_track(self, track: TrackID) -> None: ...


class IUserActivityRepository(Protocol):
    async def add(
        self,
        user_activity: UserActivityPost,
    ) -> UserActivity: ...

    async def get(
        self,
        id: int,
    ) -> UserActivity: ...

    async def list(
        self,
        filter: UserActivityFilter,
        offset: Optional[int],
        limit: Optional[int],
    ) -> list[UserActivity]: ...

    async def delete(self, filter: UserActivityFilter) -> None: ...

    async def get_most_played_tracks(
        self,
        offset: Optional[int],
        limit: Optional[int],
    ) -> MostPlayedTracks: ...

    async def get_daily_active_users_count(
        self,
        offset: Optional[int],
        limit: Optional[int],
    ) -> ActiveUsers: ...

    async def get_tracks_completion_rate(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> TracksCompletionRate: ...


class IUserRepository(Protocol):
    async def create_user(self, new_user: NewRoleUser) -> User: ...
    async def get_user_by_id(self, user: UserID) -> User: ...
    async def get_user_by_username(self, user: UserUsername) -> LoginUserWithID: ...
    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]: ...
    async def update_user(self, new_user: User) -> User: ...
    async def delete_user(self, user: UserID) -> None: ...

    async def create_playlist(self, new_playlist: NewPlaylist) -> Playlist: ...
    async def get_playlist_by_id(self, playlist: PlaylistID) -> Playlist: ...
    async def get_playlists_by_user(self, user: UserID) -> list[Playlist]: ...
    async def get_tracks_by_playlist(
        self, playlist: PlaylistID
    ) -> list[PlaylistTrack]: ...
    async def update_playlist(self, playlist: Playlist) -> Playlist: ...
    async def delete_playlist(self, playlist: PlaylistID) -> None: ...

    async def add_track_to_playlist(
        self, new_track: NewPlaylistTrack
    ) -> PlaylistTrack: ...
    async def remove_track_from_playlist(
        self, playlist_track: PlaylistTrack
    ) -> None: ...
