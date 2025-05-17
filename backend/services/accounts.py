from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from dto.accounts import (
    User,
    UserID,
    NewRoleUser,
    UserUsername,
    LoginUserWithID,
    Playlist,
    PlaylistID,
    NewPlaylist,
    PlaylistTrack,
    NewPlaylistTrack,
)
from repositories.interfaces import IUserRepository
from exceptions.accounts import (
    InvalidTokenException,
)
from typing import Optional
from sqlalchemy.exc import IntegrityError
from exceptions.accounts import UserAlreadyExist
from configs import environment as env


class AccountService:
    user_repository: IUserRepository

    def __init__(self, user_repository: IUserRepository) -> None:
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto"
        )
        self.user_repository = user_repository

    async def create_user(self, new_user: NewRoleUser) -> User:
        hashed_password = self.get_hashed_password(new_user.password)
        user_with_hashed = new_user.model_copy(update={"password": hashed_password})
        user: Optional[User] = None
        try:
            user = await self.user_repository.create_user(user_with_hashed)
        except IntegrityError as e:
            if "users_username_key" in str(e.orig):
                raise UserAlreadyExist()
            raise e
        return user

    async def get_user(self, user_id: UserID) -> User:
        return await self.user_repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: UserUsername) -> LoginUserWithID:
        return await self.user_repository.get_user_by_username(username)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return await self.user_repository.get_users(skip, limit)

    async def update_user(self, user: User) -> User:
        return await self.user_repository.update_user(user)

    async def delete_user(self, user_id: UserID) -> None:
        await self.user_repository.delete_user(user_id)

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now() + timedelta(
            minutes=env.settings.AUTH_ACCESS_TOKEN_EXPIRED_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(
            to_encode,
            key=env.settings.AUTH_SECRET_KEY,
            algorithm=env.settings.AUTH_ALGORITHM,
        )

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token,
                key=env.settings.AUTH_SECRET_KEY,
                algorithms=[env.settings.AUTH_ALGORITHM],
            )
            return payload
        except JWTError:
            return None

    def verify_password(self, entered_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(entered_password, hashed_password)

    def get_hashed_password(self, entered_password: str) -> str:
        return self.pwd_context.hash(entered_password)

    async def get_user_from_token(self, token: str) -> User:
        payload = self.verify_token(token)
        if payload is None or "sub" not in payload:
            raise InvalidTokenException()

        try:
            user_id = UserID(id=payload["sub"])
        except Exception:
            raise InvalidTokenException()

        return await self.user_repository.get_user_by_id(user_id)

    # === Playlist-related methods ===

    async def create_playlist(self, playlist: NewPlaylist) -> Playlist:
        return await self.user_repository.create_playlist(playlist)

    async def get_playlist(self, playlist_id: PlaylistID) -> Playlist:
        return await self.user_repository.get_playlist_by_id(playlist_id)

    async def get_playlist_by_user(self, user: UserID) -> list[Playlist]:
        return await self.user_repository.get_playlists_by_user(user)

    async def delete_playlist(self, playlist_id: PlaylistID) -> None:
        await self.user_repository.delete_playlist(playlist_id)

    # === PlaylistTrack-related methods ===

    async def add_track_to_playlist(self, new_track: NewPlaylistTrack) -> PlaylistTrack:
        return await self.user_repository.add_track_to_playlist(new_track)

    async def remove_track_from_playlist(self, track: PlaylistTrack) -> None:
        await self.user_repository.remove_track_from_playlist(track)

    async def get_tracks_from_playlist(
        self, playlist_id: PlaylistID
    ) -> list[PlaylistTrack]:
        return await self.user_repository.get_tracks_by_playlist(playlist_id)
