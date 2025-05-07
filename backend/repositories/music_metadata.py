from entities.music import Music
from repositories.interfaces import IMusicMetadataRepository
from models.track import Track
from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyMusicMetadataRepository(IMusicMetadataRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, music: Music) -> None:
        model = Track(
            name=music.name,
            artist_id=music.artist_id,
            album_id=music.album_id,
            audio=music.audio,
        )
        self.session.add(model)
        await self.session.commit()

    async def get(self, name: str) -> Music | None:
        result = await self.session.execute(
            select(MusicModel).where(MusicModel.name == name)
        )
        model = result.scalar_one_or_none()
        if model:
            return Music(
                id=model.id,
                name=model.name,
                artist_id=model.artist_id,
                album_id=model.album_id,
                audio=model.audio,
            )
        return None

    async def update(self, name: str, music: Music) -> None:
        await self.session.execute(
            sa_update(MusicModel)
            .where(MusicModel.name == name)
            .values(
                name=music.name,
                artist_id=music.artist_id,
                album_id=music.album_id,
                audio=music.audio,
            )
        )
        await self.session.commit()

    async def delete(self, name: str) -> None:
        await self.session.execute(sa_delete(MusicModel).where(MusicModel.name == name))
        await self.session.commit()
