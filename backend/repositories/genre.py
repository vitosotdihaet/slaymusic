from dto.music import Genre, GenreID, NewGenre, GenreSearchParams
from repositories.interfaces import IGenreRepository
from repositories.helpers import RepositoryHelpers
from models.music import GenreModel
from models.base_model import MusicModelBase
from exceptions.music import GenreNotFoundException, GenreNameAlreadyExistsException

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete, func


class SQLAlchemyGenreRepository(IGenreRepository, RepositoryHelpers):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory


    async def create_genre(self, new_genre: NewGenre) -> Genre:
        async with self.session_factory() as session:
            query = select(GenreModel).where(GenreModel.name == new_genre.name)
            model = await self._get_one_or_none(query, session)
            if model:
                raise GenreNameAlreadyExistsException(
                    f"Genre '{new_genre.name}' already exists"
                )
            genre_to_add = GenreModel(**new_genre.model_dump())
            genre_added = await self._add_and_commit(genre_to_add, session)
            return Genre.model_validate(genre_added, from_attributes=True)

    async def get_genre_by_id(self, genre: GenreID) -> Genre:
        async with self.session_factory() as session:
            query = select(GenreModel).where(GenreModel.id == genre.id)
            model = await self._get_one_or_none(query, session)
            if not model:
                raise GenreNotFoundException(f"Genre '{genre.id}' not found")
            return Genre.model_validate(model, from_attributes=True)

    async def get_genres(self, params: GenreSearchParams) -> list[Genre]:
        async with self.session_factory() as session:
            query = select(GenreModel)

            if params.name:
                query = query.filter(
                    func.similarity(GenreModel.name, params.name) >= params.threshold
                ).order_by(func.similarity(GenreModel.name, params.name).desc())

            query = query.offset(params.skip).limit(params.limit)
            models = await self._get_all(query, session)
            return [Genre.model_validate(m, from_attributes=True) for m in models]

    async def update_genre(self, new_genre: Genre) -> Genre:
        async with self.session_factory() as session:
            query = select(GenreModel).where(GenreModel.name == new_genre.name)
            model = await self._get_one_or_none(query, session)
            if model:
                raise GenreNameAlreadyExistsException(
                    f"Genre '{new_genre.name}' already exists"
                )
            model = await self._get_one_or_none(
                select(GenreModel).where(GenreModel.id == new_genre.id), session
            )
            if not model:
                raise GenreNotFoundException(f"Genre '{new_genre.id}' not found")
            updated = await self._update_and_commit(model, new_genre, session)
            return Genre.model_validate(updated, from_attributes=True)

    async def delete_genre(self, genre: GenreID) -> None:
        async with self.session_factory() as session:
            query = delete(GenreModel).where(GenreModel.id == genre.id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise GenreNotFoundException(f"Genre '{genre.id}' not found")
