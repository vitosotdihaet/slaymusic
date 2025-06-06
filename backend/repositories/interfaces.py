from dto.track_queue import (
    InQueueID,
    QueueParameters,
    QueueSrcDestIDs,
    TrackInQueueIDs,
    TrackQueue,
)
from dto.music import (
    MusicFileStats,
    Track,
    Album,
    NewAlbum,
    NewTrack,
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
from dto.user_activity import (
    UserActivity,
    UserActivityFilter,
    UserActivityPost,
)
from dto.accounts import (
    User,
    UserID,
    NewRoleUser,
    UserUsername,
    FullUser,
    NewPlaylist,
    Playlist,
    PlaylistID,
    PlaylistTrack,
    SubscribersCount,
    UserSearchParams,
    PlaylistSearchParams,
    UpdateUserRole,
    UpdatePlaylist,
    Subscribe,
    SubscribeSearchParams,
    PlaylistTrackSearchParams,
)

from typing import AsyncIterator, Protocol, Optional


class IMusicFileRepository(Protocol):
    async def save_track(
        self, track: Track, file_data: bytes, content_type: str
    ) -> None: ...

    async def save_image(
        self,
        image: Album | AlbumID | User | UserID | Playlist | PlaylistID,
        file_data: bytes,
        content_type: str,
    ) -> None: ...

    async def stream_track(
        self, track: Track, start: int, end: int
    ) -> AsyncIterator[bytes]: ...

    async def get_track_stats(self, track: Track) -> MusicFileStats: ...
    async def get_image(
        self, image: Album | AlbumID | User | UserID | Playlist | PlaylistID
    ) -> bytes: ...
    async def delete_track(self, track: Track) -> None: ...
    async def delete_image(
        self, image: Album | AlbumID | User | UserID | Playlist | PlaylistID
    ) -> None: ...


class IGenreRepository(Protocol):
    async def create_genre(self, new_genre: NewGenre) -> Genre: ...
    async def get_genre_by_id(self, genre: GenreID) -> Genre: ...
    async def get_genres(self, params: GenreSearchParams) -> list[Genre]: ...
    async def update_genre(self, new_genre: UpdateGenre) -> Genre: ...
    async def delete_genre(self, genre: GenreID) -> None: ...


class IAlbumRepository(Protocol):
    async def create_album(self, new_album: NewAlbum) -> Album: ...
    async def get_album_by_id(self, album: AlbumID) -> Album: ...
    async def get_albums(self, params: AlbumSearchParams) -> list[Album]: ...
    async def update_album(self, new_album: UpdateAlbum) -> Album: ...
    async def delete_album(self, album: AlbumID) -> None: ...


class ITrackRepository(Protocol):
    async def create_track(self, new_track: NewTrack) -> Track: ...
    async def get_track_by_id(self, track: TrackID) -> Track: ...
    async def get_tracks(self, params: TrackSearchParams) -> list[Track]: ...
    async def update_track(self, new_track: UpdateTrack) -> Track: ...
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


class IUserRepository(Protocol):
    async def create_user(self, new_user: NewRoleUser) -> User: ...
    async def get_user_by_id(self, user: UserID) -> User: ...
    async def get_user_by_username(self, user: UserUsername) -> FullUser: ...
    async def get_users(self, params: UserSearchParams) -> list[User]: ...
    async def update_user(self, new_user: UpdateUserRole) -> User: ...
    async def delete_user(self, user: UserID) -> None: ...

    async def subscribe_to(self, subscribe: Subscribe) -> None: ...
    async def unsubscribe_from(self, subscribe: Subscribe) -> None: ...
    async def get_subscriptions(self, params: SubscribeSearchParams) -> list[User]: ...
    async def get_subscribers(self, params: SubscribeSearchParams) -> list[User]: ...
    async def get_subscribe_count(self, user: UserID) -> SubscribersCount: ...


class IPlaylistRepository(Protocol):
    async def create_playlist(self, new_playlist: NewPlaylist) -> Playlist: ...
    async def get_playlist_by_id(self, playlist: PlaylistID) -> Playlist: ...
    async def get_playlists(self, params: PlaylistSearchParams) -> list[Playlist]: ...
    async def update_playlist(self, playlist: UpdatePlaylist) -> Playlist: ...
    async def delete_playlist(self, playlist: PlaylistID) -> None: ...

    async def add_track_to_playlist(
        self, playlist_track: PlaylistTrack
    ) -> PlaylistTrack: ...
    async def get_tracks_by_playlist(
        self, params: PlaylistTrackSearchParams
    ) -> list[Track]: ...
    async def remove_track_from_playlist(
        self, playlist_track: PlaylistTrack
    ) -> None: ...


class ITrackQueueRepository(Protocol):
    async def push_left(self, user_id: int, id: TrackID) -> None: ...
    async def push_right(self, user_id: int, id: TrackID) -> None: ...
    async def list(self, user_id: int, params: QueueParameters) -> TrackQueue: ...
    async def delete(self, user_id: int) -> None: ...
    async def insert(self, user_id: int, ids: TrackInQueueIDs) -> None: ...
    async def move(self, user_id: int, ids: QueueSrcDestIDs) -> None: ...
    async def remove(self, user_id: int, id: InQueueID) -> None: ...
