from dto.music import Track, NewTrack, TrackID, TrackSearchParams
from repositories.interfaces import ITrackRepository
from repositories.helpers import RepositoryHelpers
from models.music import TrackModel, AlbumModel, ArtistModel, GenreModel
from models.base_model import MusicModelBase
from configs.database import ensure_tables, ensure_extensions
from exceptions.music import (
    AlbumNotFoundException,
    ArtistNotFoundException,
    TrackNotFoundException,
    GenreNotFoundException,
)

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete, func


class SQLAlchemyTrackRepository(ITrackRepository, RepositoryHelpers):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @staticmethod
    async def create(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> "SQLAlchemyTrackRepository":
        await ensure_extensions("music")
        await ensure_tables(MusicModelBase, "music")
        return SQLAlchemyTrackRepository(session_factory)

    async def create_track(self, new_track: NewTrack) -> Track:
        async with self.session_factory() as session:
            album = await self._get_one_or_none(
                select(AlbumModel).where(AlbumModel.id == new_track.album_id), session
            )
            if not album:
                raise AlbumNotFoundException(f"Album '{new_track.album_id}' not found")
            if new_track.genre_id:
                model = await self._get_one_or_none(
                    select(GenreModel).where(GenreModel.id == new_track.genre_id),
                    session,
                )
                if not model:
                    raise GenreNotFoundException(
                        f"Genre '{new_track.genre_id}' not found"
                    )
            artist = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == new_track.artist_id),
                session,
            )
            if not artist:
                raise ArtistNotFoundException(
                    f"Artist '{new_track.artist_id}' not found"
                )
            to_add = TrackModel(**new_track.model_dump())
            added = await self._add_and_commit(to_add, session)
            return Track.model_validate(added, from_attributes=True)

    async def get_track_by_id(self, track: TrackID) -> Track:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(TrackModel).where(TrackModel.id == track.id), session
            )
            if not model:
                raise TrackNotFoundException(f"Track '{track.id}' not found")
            return Track.model_validate(model, from_attributes=True)

    async def get_tracks(self, params: TrackSearchParams) -> list[Track]:
        async with self.session_factory() as session:
            query = select(TrackModel)

            if params.artist_id:
                model = await self._get_one_or_none(
                    select(ArtistModel).where(ArtistModel.id == params.artist_id),
                    session,
                )
                if not model:
                    raise ArtistNotFoundException(
                        f"Artist '{params.artist_id}' not found"
                    )
                query = query.where(TrackModel.artist_id == params.artist_id)

            if params.album_id:
                model = await self._get_one_or_none(
                    select(AlbumModel).where(AlbumModel.id == params.album_id), session
                )
                if not model:
                    raise AlbumNotFoundException(f"Album '{params.album_id}' not found")
                query = query.where(TrackModel.album_id == params.album_id)

            if params.search_start:
                query = query.where(TrackModel.release_date >= params.search_start)

            if params.search_end:
                query = query.where(TrackModel.release_date <= params.search_end)

            if params.genre_id:
                model = await self._get_one_or_none(
                    select(GenreModel).where(GenreModel.id == params.genre_id), session
                )
                if not model:
                    raise GenreNotFoundException(f"Genre '{params.genre_id}' not found")
                query = query.where(TrackModel.genre_id == params.genre_id)

            if params.name:
                query = query.filter(
                    func.similarity(TrackModel.name, params.name) >= params.threshold
                ).order_by(func.similarity(TrackModel.name, params.name).desc())

            query = query.offset(params.skip).limit(params.limit)
            models = await self._get_all(query, session)
            return [Track.model_validate(m, from_attributes=True) for m in models]

    async def update_track(self, new_track: Track) -> Track:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == new_track.artist_id),
                session,
            )
            if not model:
                raise ArtistNotFoundException(
                    f"Artist '{new_track.artist_id}' not found"
                )
            model = await self._get_one_or_none(
                select(AlbumModel).where(AlbumModel.id == new_track.album_id),
                session,
            )
            if not model:
                raise AlbumNotFoundException(f"Album '{new_track.album_id}' not found")
            if new_track.genre_id:
                model = await self._get_one_or_none(
                    select(GenreModel).where(GenreModel.id == new_track.genre_id),
                    session,
                )
                if not model:
                    raise GenreNotFoundException(
                        f"Genre '{new_track.genre_id}' not found"
                    )
            model = await self._get_one_or_none(
                select(TrackModel).where(TrackModel.id == new_track.id), session
            )
            if not model:
                raise TrackNotFoundException(f"Track '{new_track.id}' not found")
            updated = await self._update_and_commit(model, new_track, session)
            return Track.model_validate(updated, from_attributes=True)

    async def delete_track(self, track: TrackID) -> None:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(TrackModel).where(TrackModel.id == track.id), session
            )
            if not model:
                raise TrackNotFoundException(f"Track '{track.id}' not found")

            query = delete(TrackModel).where(TrackModel.id == track.id)
            await self._delete_and_commit(query, session)

            album_id = model.album_id

            count = await session.scalar(
                select(func.count())
                .select_from(TrackModel)
                .where(TrackModel.album_id == album_id)
            )
            if count == 0:
                query = delete(AlbumModel).where(AlbumModel.id == album_id)
                await self._delete_and_commit(query, session)
