from dto.music import (
    MusicFileStats,
    SearchParams,
    Track,
    Artist,
    Album,
    NewAlbum,
    NewArtist,
    NewTrack,
    ArtistID,
    AlbumID,
    TrackID,
)
from dto.user_activity import (
    ActiveUsers,
    TracksCompletionRate,
    UserActivity,
    MostPlayedTracks,
    UserActivityFilter,
    UserActivityPost,
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


class IArtistRepository(Protocol):
    async def create_artist(self, new_artist: NewArtist) -> Artist: ...
    async def get_artist_by_id(self, artist: ArtistID) -> Artist: ...
    async def get_artists(self, params: SearchParams) -> list[Artist]: ...
    async def update_artist(self, new_artist: Artist) -> Artist: ...
    async def delete_artist(self, artist: ArtistID) -> None: ...


class IAlbumRepository(Protocol):
    async def create_album(self, new_album: NewAlbum) -> Album: ...
    async def get_album_by_id(self, album: AlbumID) -> Album: ...
    async def get_albums_by_artist(
        self, artist: ArtistID, params: SearchParams
    ) -> list[Album]: ...
    async def get_albums(self, params: SearchParams) -> list[Album]: ...
    async def update_album(self, new_album: Album) -> Album: ...
    async def delete_album(self, album: AlbumID) -> None: ...


class ITrackRepository(Protocol):
    async def create_track(self, new_track: NewTrack) -> Track: ...
    async def get_track_by_id(self, track: TrackID) -> Track: ...
    async def get_tracks_by_artist(
        self, artist: ArtistID, params: SearchParams
    ) -> list[Track]: ...
    async def get_tracks_by_album(
        self, album: AlbumID, params: SearchParams
    ) -> list[Track]: ...
    async def get_tracks(self, params: SearchParams) -> list[Track]: ...
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
