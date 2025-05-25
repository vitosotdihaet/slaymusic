from dto.music import Album, NewAlbum, AlbumID, AlbumSearchParams, UpdateAlbum
from repositories.interfaces import IAlbumRepository
from repositories.helpers import RepositoryHelpers
from models.album import AlbumModel
from models.user import UserModel
from exceptions.music import AlbumNotFoundException
from exceptions.accounts import UserNotFoundException

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete, func


class SQLAlchemyAlbumRepository(IAlbumRepository, RepositoryHelpers):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create_album(self, new_album: NewAlbum) -> Album:
        async with self.session_factory() as session:
            artist = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == new_album.artist_id),
                session,
            )
            if not artist:
                raise UserNotFoundException(f"Artist '{new_album.artist_id}' not found")
            to_add = AlbumModel(**new_album.model_dump())
            added = await self._add_and_commit(to_add, session)
            return Album.model_validate(added, from_attributes=True)

    async def get_album_by_id(self, album: AlbumID) -> Album:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(AlbumModel).where(AlbumModel.id == album.id), session
            )
            if not model:
                raise AlbumNotFoundException(f"Album '{album.id}' not found")
            return Album.model_validate(model, from_attributes=True)

    async def get_albums(self, params: AlbumSearchParams) -> list[Album]:
        async with self.session_factory() as session:
            query = select(AlbumModel)

            if params.artist_id:
                model = await self._get_one_or_none(
                    select(UserModel).where(UserModel.id == params.artist_id),
                    session,
                )
                if not model:
                    raise UserNotFoundException(
                        f"Artist '{params.artist_id}' not found"
                    )
                query = query.where(AlbumModel.artist_id == params.artist_id)

            if params.release_search_start:
                query = query.where(AlbumModel.release_date >= params.search_start)

            if params.release_search_end:
                query = query.where(AlbumModel.release_date <= params.search_end)

            if params.created_search_start:
                query = query.where(
                    AlbumModel.created_at >= params.created_search_start
                )
            if params.created_search_end:
                query = query.where(AlbumModel.created_at <= params.created_search_end)
            if params.updated_search_start:
                query = query.where(
                    AlbumModel.updated_at >= params.updated_search_start
                )
            if params.updated_search_end:
                query = query.where(AlbumModel.updated_at <= params.updated_search_end)

            if params.name:
                query = query.filter(
                    func.similarity(AlbumModel.name, params.name) >= params.threshold
                ).order_by(func.similarity(AlbumModel.name, params.name).desc())

            query = query.offset(params.skip).limit(params.limit)
            models = await self._get_all(query, session)
            return [Album.model_validate(m, from_attributes=True) for m in models]

    async def update_album(self, new_album: UpdateAlbum) -> Album:
        async with self.session_factory() as session:
            if new_album.artist_id:
                model = await self._get_one_or_none(
                    select(UserModel).where(UserModel.id == new_album.artist_id),
                    session,
                )
                if not model:
                    raise UserNotFoundException(
                        f"Artist '{new_album.artist_id}' not found"
                    )
            model = await self._get_one_or_none(
                select(AlbumModel).where(AlbumModel.id == new_album.id), session
            )
            if not model:
                raise AlbumNotFoundException(f"Album '{new_album.id}' not found")
            updated = await self._update_and_commit(model, new_album, session)
            return Album.model_validate(updated, from_attributes=True)

    async def delete_album(self, album: AlbumID) -> None:
        async with self.session_factory() as session:
            query = delete(AlbumModel).where(AlbumModel.id == album.id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise AlbumNotFoundException(f"Album '{album.id}' not found")
