from dto.music import Track
from repositories.interfaces import IMusicMetadataRepository
from models.music import MusicBase, TrackModel, AlbumModel, ArtistModel
from configs.database import ensure_tables
from exceptions.music import MusicFileNotFoundException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete


class SQLAlchemyMusicMetadataRepository(IMusicMetadataRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        session: AsyncSession,
    ) -> "SQLAlchemyMusicMetadataRepository":
        await ensure_tables(MusicBase, "music")
        return SQLAlchemyMusicMetadataRepository(session)

    async def add(self, track: Track) -> None:
        model = TrackModel(
            name=track.name,
            artist_id=track.artist_id,
            album_id=track.album_id,
            picture_path=track.picture_path,
        )
        self.session.add(model)
        await self.session.commit()

    async def get(self, name: str) -> Track | None:
        stmt = select(TrackModel).where(TrackModel.name == name)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            return Track(
                name=model.name,
                artist=model.artist,
                album=model.album,
                picture_path=model.picture_path,
            )
        raise MusicFileNotFoundException(f"Metadata for '{model.name}' not found")

    async def update(self, name: str, track: Track) -> None:
        stmt = (
            update(TrackModel)
            .where(TrackModel.name == name)
            .values(
                name=track.name,
                artist=track.artist,
                album=track.album,
                picture_path=track.picture_path,
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, name: str) -> None:
        stmt = delete(TrackModel).where(TrackModel.name == name)
        await self.session.execute(stmt)
        await self.session.commit()
