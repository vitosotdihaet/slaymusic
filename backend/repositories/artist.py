from dto.music import Artist, NewArtist, ArtistID, ArtistSearchParams
from repositories.interfaces import IArtistRepository
from repositories.helpers import RepositoryHelpers
from models.music import ArtistModel
from models.base_model import MusicModelBase
from configs.database import ensure_tables, ensure_extensions
from exceptions.music import ArtistNotFoundException

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete, func


class SQLAlchemyArtistRepository(IArtistRepository, RepositoryHelpers):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @staticmethod
    async def create(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> "SQLAlchemyArtistRepository":
        await ensure_extensions("music")
        await ensure_tables(MusicModelBase, "music")
        return SQLAlchemyArtistRepository(session_factory)

    async def create_artist(self, new_artist: NewArtist) -> Artist:
        async with self.session_factory() as session:
            artist_to_add = ArtistModel(**new_artist.model_dump())
            artist_added = await self._add_and_commit(artist_to_add, session)
            return Artist.model_validate(artist_added, from_attributes=True)

    async def get_artist_by_id(self, artist: ArtistID) -> Artist:
        async with self.session_factory() as session:
            query = select(ArtistModel).where(ArtistModel.id == artist.id)
            model = await self._get_one_or_none(query, session)
            if not model:
                raise ArtistNotFoundException(f"Artist '{artist.id}' not found")
            return Artist.model_validate(model, from_attributes=True)

    async def get_artists(self, params: ArtistSearchParams) -> list[Artist]:
        async with self.session_factory() as session:
            query = select(ArtistModel)

            if params.name:
                query = query.filter(
                    func.similarity(ArtistModel.name, params.name) >= params.threshold
                ).order_by(func.similarity(ArtistModel.name, params.name).desc())

            query = query.offset(params.skip).limit(params.limit)
            models = await self._get_all(query, session)
            return [Artist.model_validate(m, from_attributes=True) for m in models]

    async def update_artist(self, new_artist: Artist) -> Artist:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == new_artist.id), session
            )
            if not model:
                raise ArtistNotFoundException(f"Artist '{new_artist.id}' not found")
            updated = await self._update_and_commit(model, new_artist, session)
            return Artist.model_validate(updated, from_attributes=True)

    async def delete_artist(self, artist: ArtistID) -> None:
        async with self.session_factory() as session:
            query = delete(ArtistModel).where(ArtistModel.id == artist.id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise ArtistNotFoundException(f"Artist '{artist.id}' not found")
