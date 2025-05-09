from dto.music import Artist
from repositories.interfaces import IMusicArtistRepository
from models.music import MusicBase, ArtistModel
from configs.database import ensure_tables
from exceptions.music import ArtistNotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


class SQLAlchemyMusicArtistRepository(IMusicArtistRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        session: AsyncSession,
    ) -> "SQLAlchemyMusicArtistRepository":
        await ensure_tables(MusicBase, "music")
        return SQLAlchemyMusicArtistRepository(session)

    async def add(self, artist: Artist) -> None:
        model = ArtistModel(
            artist_name = artist.artist_name,
            artist_picture_path = artist.artist_picture_path,
        )
        self.session.add(model)
        await self.session.commit()

    async def get(self, artist_id: int) -> Artist | None:
        stmt = select(ArtistModel).where(ArtistModel.artist_id == artist_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            return Artist(
                artist_name=model.artist_name,
                artist_picture_path=model.artist_picture_path,
            )
        raise ArtistNotFoundException(f"Artist with artist_id {model.artist_id} not found")

    async def update(self, artist_id: int, artist: Artist) -> None:
        stmt = (
            update(ArtistModel)
            .where(ArtistModel.artist_id == artist_id)
            .values(
                artist_name=artist.artist_name,
                artist_picture_path=artist.artist_picture_path,
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, artist_id: int) -> None:
        stmt = delete(ArtistModel).where(ArtistModel.artist_id == artist_id)
        await self.session.execute(stmt)
        await self.session.commit()
