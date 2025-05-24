from dto.accounts import (
    Playlist,
    PlaylistID,
    NewPlaylist,
    PlaylistSearchParams,
    PlaylistTrack,
    UpdatePlaylist,
)
from repositories.interfaces import IPlaylistRepository
from repositories.helpers import RepositoryHelpers
from models.playlist import PlaylistModel
from models.user import UserModel
from models.playlist_track import PlaylistTrackModel
from models.track import TrackModel
from exceptions.music import TrackNotFoundException
from exceptions.accounts import (
    PlaylistNotFoundException,
    UserNotFoundException,
    PlaylistTrackNotFoundException,
    PlaylistAlreadyExist,
)

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete, func


class SQLAlchemyPlaylistRepository(IPlaylistRepository, RepositoryHelpers):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create_playlist(self, new_playlist: NewPlaylist) -> Playlist:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == new_playlist.author_id), session
            )
            if not model:
                raise UserNotFoundException(
                    f"User '{new_playlist.author_id}' not found"
                )
            to_add = PlaylistModel(**new_playlist.model_dump())
            added = await self._add_and_commit(to_add, session)
            return Playlist.model_validate(added, from_attributes=True)

    async def get_playlist_by_id(self, playlist: PlaylistID) -> Playlist:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(PlaylistModel).where(PlaylistModel.id == playlist.id), session
            )
            if not model:
                raise PlaylistNotFoundException(f"Playlist '{playlist.id}' not found")
            return Playlist.model_validate(model, from_attributes=True)

    async def get_playlists(self, params: PlaylistSearchParams) -> list[Playlist]:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == params.author_id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{params.author_id}' not found")
            query = select(PlaylistModel).where(
                PlaylistModel.author_id == params.author_id
            )

            if params.name:
                query = query.filter(
                    func.similarity(PlaylistModel.name, params.name) >= params.threshold
                ).order_by(func.similarity(PlaylistModel.name, params.name).desc())

            if params.created_search_start:
                query = query.where(
                    PlaylistModel.created_at >= params.created_search_start
                )
            if params.created_search_end:
                query = query.where(
                    PlaylistModel.created_at <= params.created_search_end
                )
            if params.updated_search_start:
                query = query.where(
                    PlaylistModel.updated_at >= params.updated_search_start
                )
            if params.updated_search_end:
                query = query.where(
                    PlaylistModel.updated_at <= params.updated_search_end
                )

            query = query.offset(params.skip).limit(params.limit)
            models = await self._get_all(query, session)
            return [Playlist.model_validate(m, from_attributes=True) for m in models]

    async def update_playlist(self, playlist: UpdatePlaylist) -> Playlist:
        async with self.session_factory() as session:
            existing = await self._get_one_or_none(
                select(PlaylistModel).where(PlaylistModel.id == playlist.id), session
            )
            if not existing:
                raise PlaylistNotFoundException(f"Playlist '{playlist.id}' not found")
            if playlist.author_id:
                model = await self._get_one_or_none(
                    select(UserModel).where(UserModel.id == playlist.author_id), session
                )
                if not model:
                    raise UserNotFoundException(
                        f"User '{playlist.author_id}' not found"
                    )
            updated = await self._update_and_commit(existing, playlist, session)
            return Playlist.model_validate(updated, from_attributes=True)

    async def delete_playlist(self, playlist: PlaylistID) -> None:
        async with self.session_factory() as session:
            query = delete(PlaylistModel).where(PlaylistModel.id == playlist.id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise PlaylistNotFoundException(f"Playlist '{playlist.id}' not found")

    async def add_track_to_playlist(
        self, playlist_track: PlaylistTrack
    ) -> PlaylistTrack:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(PlaylistTrackModel).where(
                    PlaylistTrackModel.playlist_id == playlist_track.playlist_id,
                    PlaylistTrackModel.track_id == playlist_track.track_id,
                ),
                session,
            )
            if model:
                raise PlaylistAlreadyExist(
                    f"Playlist '{playlist_track.playlist_id}' already has track '{playlist_track.track_id}'"
                )
            model = await self._get_one_or_none(
                select(PlaylistModel).where(
                    PlaylistModel.id == playlist_track.playlist_id
                ),
                session,
            )
            if not model:
                raise PlaylistNotFoundException(
                    f"Playlist '{playlist_track.playlist_id}' not found"
                )
            model = await self._get_one_or_none(
                select(TrackModel).where(TrackModel.id == playlist_track.track_id),
                session,
            )
            if not model:
                raise TrackNotFoundException(
                    f"Track '{playlist_track.track_id}' not found"
                )

            to_add = PlaylistTrackModel(**playlist_track.model_dump())
            added = await self._add_and_commit(to_add, session)
            return PlaylistTrack.model_validate(added, from_attributes=True)

    async def remove_track_from_playlist(self, playlist_track: PlaylistTrack) -> None:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(PlaylistModel).where(
                    PlaylistModel.id == playlist_track.playlist_id
                ),
                session,
            )
            if not model:
                raise PlaylistNotFoundException(
                    f"Playlist '{playlist_track.playlist_id}' not found"
                )
            model = await self._get_one_or_none(
                select(TrackModel).where(TrackModel.id == playlist_track.track_id),
                session,
            )
            if not model:
                raise TrackNotFoundException(
                    f"Track '{playlist_track.track_id}' not found"
                )

            query = delete(PlaylistTrackModel).where(
                (PlaylistTrackModel.playlist_id == playlist_track.playlist_id)
                & (PlaylistTrackModel.track_id == playlist_track.track_id)
            )
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise PlaylistTrackNotFoundException(
                    f"Playlist '{playlist_track.playlist_id}' don't have track '{playlist_track.track_id}'"
                )
