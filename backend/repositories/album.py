from dto.music import Album, NewAlbum, AlbumID, ArtistID
from repositories.interfaces import IAlbumRepository
from repositories.base_music_metadata import SQLAlchemyBaseMusicMetadataRepository
from models.music import MusicBase, AlbumModel, ArtistModel
from configs.database import ensure_tables
from exceptions.music import AlbumNotFoundException, ArtistNotFoundException

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete


class SQLAlchemyAlbumRepository(
    IAlbumRepository, SQLAlchemyBaseMusicMetadataRepository
):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @staticmethod
    async def create(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> "SQLAlchemyAlbumRepository":
        await ensure_tables(MusicBase, "music")
        return SQLAlchemyAlbumRepository(session_factory)

    async def create_album(self, new_album: NewAlbum) -> Album:
        async with self.session_factory() as session:
            artist = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == new_album.artist_id),
                session,
            )
            if not artist:
                raise ArtistNotFoundException(
                    f"Artist '{new_album.artist_id}' not found"
                )
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

    async def get_albums_by_artist(
        self, artist: ArtistID, skip: int = 0, limit: int = 100
    ) -> list[Album]:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == artist.id), session
            )
            if not model:
                raise ArtistNotFoundException(f"Artist '{artist.id}' not found")
            query = (
                select(AlbumModel)
                .where(AlbumModel.artist_id == artist.id)
                .offset(skip)
                .limit(limit)
            )
            models = await self._get_all(query, session)
            return [Album.model_validate(m, from_attributes=True) for m in models]

    async def get_albums(self, skip: int = 0, limit: int = 100) -> list[Album]:
        async with self.session_factory() as session:
            query = select(AlbumModel).offset(skip).limit(limit)
            models = await self._get_all(query, session)
            return [Album.model_validate(m, from_attributes=True) for m in models]

    async def update_album(self, new_album: Album) -> Album:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == new_album.artist_id),
                session,
            )
            if not model:
                raise ArtistNotFoundException(
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
