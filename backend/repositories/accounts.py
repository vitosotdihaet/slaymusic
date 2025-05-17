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
from repositories.interfaces import IUserRepository
from repositories.helpers import RepositoryHelpers
from models.accounts import UserModel, PlaylistModel, PlaylistTrackModel
from models.base_model import AccountsModelBase
from configs.database import ensure_tables
from exceptions.accounts import UserNotFoundException, PlaylistNotFoundException

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete


class SQLAlchemyUserRepository(IUserRepository, RepositoryHelpers):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @staticmethod
    async def create(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> "SQLAlchemyUserRepository":
        await ensure_tables(AccountsModelBase, "accounts")
        return SQLAlchemyUserRepository(session_factory)

    # --- USER METHODS ---
    async def create_user(self, new_user: NewRoleUser) -> User:
        async with self.session_factory() as session:
            to_add = UserModel(**new_user.model_dump())
            added = await self._add_and_commit(to_add, session)
            return User.model_validate(added, from_attributes=True)

    async def get_user_by_id(self, user: UserID) -> User:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == user.id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{user.id}' not found")
            return User.model_validate(model, from_attributes=True)

    async def get_user_by_username(self, user: UserUsername) -> LoginUserWithID:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.username == user.username), session
            )
            if not model:
                raise UserNotFoundException(f"User '{user.username}' not found")
            return LoginUserWithID.model_validate(model, from_attributes=True)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        async with self.session_factory() as session:
            query = select(UserModel).offset(skip).limit(limit)
            models = await self._get_all(query, session)
            return [User.model_validate(m, from_attributes=True) for m in models]

    async def update_user(self, new_user: User) -> User:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == new_user.id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{new_user.id}' not found")
            updated = await self._update_and_commit(model, new_user, session)
            return User.model_validate(updated, from_attributes=True)

    async def delete_user(self, user: UserID) -> None:
        async with self.session_factory() as session:
            query = delete(UserModel).where(UserModel.id == user.id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise UserNotFoundException(f"User '{user.id}' not found")

    # --- PLAYLIST METHODS ---
    async def create_playlist(self, new_pl: NewPlaylist) -> Playlist:
        async with self.session_factory() as session:
            to_add = PlaylistModel(**new_pl.model_dump())
            added = await self._add_and_commit(to_add, session)
            return Playlist.model_validate(added, from_attributes=True)

    async def get_playlist_by_id(self, playlist: PlaylistID) -> Playlist:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(PlaylistModel).where(
                    PlaylistModel.playlist_id == playlist.playlist_id
                ),
                session,
            )
            if not model:
                raise PlaylistNotFoundException(
                    f"Playlist '{playlist.playlist_id}' not found"
                )
            return Playlist.model_validate(model, from_attributes=True)

    async def get_playlists_by_user(self, user: UserID) -> list[Playlist]:
        async with self.session_factory() as session:
            query = select(PlaylistModel).where(PlaylistModel.author_id == user.id)
            models = await self._get_all(query, session)
            return [Playlist.model_validate(m, from_attributes=True) for m in models]

    async def get_tracks_by_playlist(self, playlist: PlaylistID) -> list[PlaylistTrack]:
        async with self.session_factory() as session:
            query = select(PlaylistTrackModel).where(
                PlaylistModel.playlist_id == playlist.playlist_id
            )
            models = await self._get_all(query, session)
            return [
                PlaylistTrack.model_validate(m, from_attributes=True) for m in models
            ]

    async def update_playlist(self, pl: Playlist) -> Playlist:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(PlaylistModel).where(
                    PlaylistModel.playlist_id == pl.playlist_id
                ),
                session,
            )
            if not model:
                raise PlaylistNotFoundException(
                    f"Playlist '{pl.playlist_id}' not found"
                )
            updated = await self._update_and_commit(model, pl, session)
            return Playlist.model_validate(updated, from_attributes=True)

    async def delete_playlist(self, playlist: PlaylistID) -> None:
        async with self.session_factory() as session:
            query = delete(PlaylistModel).where(
                PlaylistModel.playlist_id == playlist.playlist_id
            )
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise PlaylistNotFoundException(
                    f"Playlist '{playlist.playlist_id}' not found"
                )

    async def add_track_to_playlist(self, new_pt: NewPlaylistTrack) -> PlaylistTrack:
        async with self.session_factory() as session:
            to_add = PlaylistTrackModel(**new_pt.model_dump())
            added = await self._add_and_commit(to_add, session)
            return PlaylistTrack.model_validate(added, from_attributes=True)

    async def remove_track_from_playlist(self, pt: PlaylistTrack) -> None:
        async with self.session_factory() as session:
            query = delete(PlaylistTrackModel).where(
                PlaylistTrackModel.playlist_id == pt.playlist_id,
                PlaylistTrackModel.track_id == pt.track_id,
            )
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise PlaylistNotFoundException(
                    f"Track {pt.track_id} not found in playlist {pt.playlist_id}"
                )
