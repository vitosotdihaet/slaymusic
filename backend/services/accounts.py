from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from dto.accounts import (
    User,
    UserID,
    NewRoleUser,
    UserUsername,
    UserMiddleware,
    FullUser,
    Playlist,
    PlaylistID,
    NewPlaylist,
    PlaylistTrack,
    UserSearchParams,
    SubscribersCount,
    PlaylistSearchParams,
    Artist,
    Subscribe,
    UpdateUser,
    UpdatePlaylist,
    SubscribeSearchParams,
    ArtistSearchParams,
    UpdateUserRole,
)
from dto.music import AlbumSearchParams, TrackSearchParams, AlbumID, TrackID
from repositories.interfaces import (
    IUserRepository,
    IPlaylistRepository,
    IMusicFileRepository,
    IAlbumRepository,
    ITrackRepository,
)
from exceptions.music import ImageFileNotFoundException
from typing import Optional
from configs import environment as env


class AccountService:
    user_repository: IUserRepository
    playlist_repository: IPlaylistRepository
    music_file_repository: IMusicFileRepository
    album_repository: IAlbumRepository
    track_repository: ITrackRepository

    def __init__(
        self,
        user_repository: IUserRepository,
        playlist_repository: IPlaylistRepository,
        music_file_repository: IMusicFileRepository,
        album_repository: IAlbumRepository,
        track_repository: ITrackRepository,
    ) -> None:
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto"
        )
        self.user_repository = user_repository
        self.playlist_repository = playlist_repository
        self.music_file_repository = music_file_repository
        self.album_repository = album_repository
        self.track_repository = track_repository

    async def create_user(
        self,
        new_user: NewRoleUser,
        image_data: bytes | None = None,
        image_content_type: str | None = None,
    ) -> User:
        hashed_password = self.get_hashed_password(new_user.password)
        user_with_hashed = new_user.model_copy(update={"password": hashed_password})
        user = await self.user_repository.create_user(user_with_hashed)
        if image_content_type:
            await self.music_file_repository.save_image(
                user, image_data, image_content_type
            )
        return user

    async def get_user(self, user_id: UserID) -> User:
        return await self.user_repository.get_user_by_id(user_id)

    async def get_user_artist(self, user_id: UserID) -> Artist:
        user = await self.user_repository.get_user_by_id(user_id)
        return Artist.model_validate(user.model_dump())

    async def get_user_image(self, user_id: UserID) -> bytes:
        await self.user_repository.get_user_by_id(user_id)
        return await self.music_file_repository.get_image(user_id)

    async def get_user_by_username(self, username: UserUsername) -> FullUser:
        return await self.user_repository.get_user_by_username(username)

    async def get_users(self, params: UserSearchParams) -> list[User]:
        return await self.user_repository.get_users(params)

    async def get_users_artists(self, params: ArtistSearchParams) -> list[Artist]:
        users = await self.user_repository.get_users(
            UserSearchParams.model_validate(params.model_dump())
        )
        return [Artist.model_validate(u.model_dump()) for u in users]

    async def update_user(self, user: UpdateUser) -> User:
        return await self.user_repository.update_user(
            UpdateUserRole.model_validate(user.model_dump())
        )

    async def update_user_with_role(self, user: UpdateUserRole) -> User:
        return await self.user_repository.update_user(user)

    async def update_user_image(
        self,
        user_id: UserID,
        image_data: bytes,
        image_content_type: str,
    ):
        await self.user_repository.get_user_by_id(user_id)
        await self.music_file_repository.save_image(
            user_id, image_data, image_content_type
        )

    async def delete_user(self, user_id: UserID) -> None:
        playlists = await self.get_playlists(
            PlaylistSearchParams(author_id=user_id.id, limit=10000)
        )
        for playlist in playlists:
            await self.delete_playlist(PlaylistID(id=playlist.id))

        albums = await self.album_repository.get_albums(
            AlbumSearchParams(artist_id=user_id.id, limit=10000)
        )
        for album in albums:
            tracks = await self.track_repository.get_tracks(
                TrackSearchParams(album_id=album.id, limit=10000)
            )
            for track in tracks:
                await self.music_file_repository.delete_track(track)
                await self.track_repository.delete_track(TrackID(id=track.id))
            try:
                await self.music_file_repository.delete_image(AlbumID(id=album.id))
            except ImageFileNotFoundException:
                pass

        await self.user_repository.delete_user(user_id)
        try:
            await self.music_file_repository.delete_image(user_id)
        except ImageFileNotFoundException:
            pass

    async def delete_user_image(self, user_id: UserID) -> None:
        await self.user_repository.get_user_by_id(user_id)
        await self.music_file_repository.delete_image(user_id)

    def create_access_token(self, data: UserMiddleware) -> str:
        expire = datetime.now() + timedelta(
            minutes=env.settings.AUTH_ACCESS_TOKEN_EXPIRED_MINUTES
        )
        to_encode = data.model_dump()
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            key=env.settings.AUTH_SECRET_KEY,
            algorithm=env.settings.AUTH_ALGORITHM,
        )

    def verify_token(self, token: str) -> Optional[UserMiddleware]:
        try:
            payload = jwt.decode(
                token,
                key=env.settings.AUTH_SECRET_KEY,
                algorithms=[env.settings.AUTH_ALGORITHM],
            )

            return UserMiddleware(**payload)
        except JWTError:
            return None

    def verify_password(self, entered_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(entered_password, hashed_password)

    def get_hashed_password(self, entered_password: str) -> str:
        return self.pwd_context.hash(entered_password)

    # === Subscription-related methods ===

    async def subscribe_to(self, subscribe: Subscribe) -> None:
        await self.user_repository.subscribe_to(subscribe)

    async def unsubscribe_from(self, subscribe: Subscribe) -> None:
        await self.user_repository.unsubscribe_from(subscribe)

    async def get_subscriptions(self, params: SubscribeSearchParams) -> list[Artist]:
        users = await self.user_repository.get_subscriptions(params)
        return [Artist.model_validate(u.model_dump()) for u in users]

    async def get_subscribers(self, params: SubscribeSearchParams) -> list[Artist]:
        users = await self.user_repository.get_subscribers(params)
        return [Artist.model_validate(u.model_dump()) for u in users]

    async def get_subscribe_count(self, user: UserID) -> SubscribersCount:
        return await self.user_repository.get_subscribe_count(user)

    # === Playlist-related methods ===

    async def create_playlist(
        self,
        playlist: NewPlaylist,
        image_data: bytes | None = None,
        image_content_type: str | None = None,
    ) -> Playlist:
        playlist = await self.playlist_repository.create_playlist(playlist)
        if image_content_type:
            await self.music_file_repository.save_image(
                playlist, image_data, image_content_type
            )
        return playlist

    async def get_playlist(self, playlist_id: PlaylistID) -> Playlist:
        return await self.playlist_repository.get_playlist_by_id(playlist_id)

    async def get_playlists(self, params: PlaylistSearchParams) -> list[Playlist]:
        return await self.playlist_repository.get_playlists(params)

    async def get_playlist_image(self, playlist_id: PlaylistID) -> bytes:
        await self.playlist_repository.get_playlist_by_id(playlist_id)
        return await self.music_file_repository.get_image(playlist_id)

    async def update_playlist(self, playlist: UpdatePlaylist) -> Playlist:
        return await self.playlist_repository.update_playlist(playlist)

    async def update_playlist_image(
        self,
        playlist_id: PlaylistID,
        image_data: bytes,
        image_content_type: str,
    ) -> None:
        await self.playlist_repository.get_playlist_by_id(playlist_id)
        await self.music_file_repository.save_image(
            playlist_id, image_data, image_content_type
        )

    async def delete_playlist(self, playlist_id: PlaylistID) -> None:
        await self.playlist_repository.delete_playlist(playlist_id)
        try:
            await self.music_file_repository.delete_image(playlist_id)
        except ImageFileNotFoundException:
            pass

    async def delete_playlist_image(self, playlist_id: PlaylistID) -> None:
        await self.playlist_repository.get_playlist_by_id(playlist_id)
        await self.music_file_repository.delete_image(playlist_id)

    # === PlaylistTrack-related methods ===

    async def add_track_to_playlist(
        self, playlist_track: PlaylistTrack
    ) -> PlaylistTrack:
        return await self.playlist_repository.add_track_to_playlist(playlist_track)

    async def remove_track_from_playlist(self, playlist_track: PlaylistTrack) -> None:
        await self.playlist_repository.remove_track_from_playlist(playlist_track)
