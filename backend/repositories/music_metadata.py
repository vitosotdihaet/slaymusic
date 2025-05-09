from dto.music import Track, Artist, Album, NewAlbum, NewArtist, NewTrack
from repositories.interfaces import IMusicMetadataRepository
from models.music import MusicBase, TrackModel, AlbumModel, ArtistModel
from configs.database import ensure_tables
from exceptions.music import (
    AlbumNotFoundException,
    ArtistNotFoundException,
    TrackNotFoundException,
)

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete


class SQLAlchemyMusicMetadataRepository(IMusicMetadataRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> "SQLAlchemyMusicMetadataRepository":
        await ensure_tables(MusicBase, "music")
        return SQLAlchemyMusicMetadataRepository(session_factory)

    # Helpers
    async def _execute_query(self, query, session: AsyncSession):
        result = await session.execute(query)
        return result

    async def _get_one_or_none(self, query, session: AsyncSession):
        result = await session.execute(query)
        return result.scalars().one_or_none()

    async def _get_all(self, query, session: AsyncSession):
        result = await session.execute(query)
        return result.scalars().all()

    async def _add_and_commit(self, instance, session: AsyncSession):
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def _update_and_commit(self, instance, new_data, session: AsyncSession):
        for field, value in new_data.model_dump().items():
            setattr(instance, field, value)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def _delete_and_commit(self, query, session: AsyncSession) -> int:
        result = await session.execute(query)
        await session.commit()
        return result.rowcount

    # Artist
    async def create_artist(self, new_artist: NewArtist) -> Artist:
        async with self.session_factory() as session:
            artist_to_add = ArtistModel(**new_artist.model_dump())
            artist_added = await self._add_and_commit(artist_to_add, session)
            return Artist.model_validate(artist_added, from_attributes=True)

    async def get_artist_by_id(self, artist_id: int) -> Artist:
        async with self.session_factory() as session:
            query = select(ArtistModel).where(ArtistModel.id == artist_id)
            model = await self._get_one_or_none(query, session)
            if not model:
                raise ArtistNotFoundException(artist_id)
            return Artist.model_validate(model, from_attributes=True)

    async def get_all_artists(self, skip: int = 0, limit: int = 100) -> list[Artist]:
        async with self.session_factory() as session:
            query = select(ArtistModel).offset(skip).limit(limit)
            models = await self._get_all(query, session)
            return [Artist.model_validate(m, from_attributes=True) for m in models]

    async def update_artist(self, artist_id: int, new_data: NewArtist) -> Artist:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == artist_id), session
            )
            if not model:
                raise ArtistNotFoundException(artist_id)
            updated = await self._update_and_commit(model, new_data, session)
            return Artist.model_validate(updated, from_attributes=True)

    async def delete_artist(self, artist_id: int) -> None:
        async with self.session_factory() as session:
            query = delete(ArtistModel).where(ArtistModel.id == artist_id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise ArtistNotFoundException(artist_id)

    # Album
    async def create_album(self, new_album: NewAlbum) -> Album:
        async with self.session_factory() as session:
            artist = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == new_album.artist_id),
                session,
            )
            if not artist:
                raise ArtistNotFoundException(new_album.artist_id)
            to_add = AlbumModel(**new_album.model_dump())
            added = await self._add_and_commit(to_add, session)
            return Album.model_validate(added, from_attributes=True)

    async def get_album_by_id(self, album_id: int) -> Album:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(AlbumModel).where(AlbumModel.id == album_id), session
            )
            if not model:
                raise AlbumNotFoundException(album_id)
            return Album.model_validate(model, from_attributes=True)

    async def get_albums_by_artist(
        self, artist_id: int, skip: int = 0, limit: int = 100
    ) -> list[Album]:
        async with self.session_factory() as session:
            query = (
                select(AlbumModel)
                .where(AlbumModel.artist_id == artist_id)
                .offset(skip)
                .limit(limit)
            )
            models = await self._get_all(query, session)
            return [Album.model_validate(m, from_attributes=True) for m in models]

    async def update_album(self, album_id: int, new_data: NewAlbum) -> Album:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(AlbumModel).where(AlbumModel.id == album_id), session
            )
            if not model:
                raise AlbumNotFoundException(album_id)
            updated = await self._update_and_commit(model, new_data, session)
            return Album.model_validate(updated, from_attributes=True)

    async def delete_album(self, album_id: int) -> None:
        async with self.session_factory() as session:
            query = delete(AlbumModel).where(AlbumModel.id == album_id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise AlbumNotFoundException(album_id)

    # Track
    async def create_track(self, new_track: NewTrack) -> Track:
        async with self.session_factory() as session:
            album = await self._get_one_or_none(
                select(AlbumModel).where(AlbumModel.id == new_track.album_id), session
            )
            if not album:
                raise AlbumNotFoundException(new_track.album_id)
            artist = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == new_track.artist_id),
                session,
            )
            if not artist:
                raise ArtistNotFoundException(new_track.artist_id)
            to_add = TrackModel(**new_track.model_dump())
            added = await self._add_and_commit(to_add, session)
            return Track.model_validate(added, from_attributes=True)

    async def get_track_by_id(self, track_id: int) -> Track:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(TrackModel).where(TrackModel.id == track_id), session
            )
            if not model:
                raise TrackNotFoundException(track_id)
            return Track.model_validate(model, from_attributes=True)

    async def get_tracks_by_artist(
        self, artist_id: int, skip: int = 0, limit: int = 100
    ) -> list[Track]:
        async with self.session_factory() as session:
            query = (
                select(TrackModel)
                .where(TrackModel.artist_id == artist_id)
                .offset(skip)
                .limit(limit)
            )
            models = await self._get_all(query, session)
            return [Track.model_validate(m, from_attributes=True) for m in models]

    async def get_tracks(self, skip: int = 0, limit: int = 100) -> list[Track]:
        async with self.session_factory() as session:
            query = select(TrackModel).offset(skip).limit(limit)
            models = await self._get_all(query, session)
            return [Track.model_validate(m, from_attributes=True) for m in models]

    async def get_tracks_by_album(
        self, album_id: int, skip: int = 0, limit: int = 100
    ) -> list[Track]:
        async with self.session_factory() as session:
            query = (
                select(TrackModel)
                .where(TrackModel.album_id == album_id)
                .offset(skip)
                .limit(limit)
            )
            models = await self._get_all(query, session)
            return [Track.model_validate(m, from_attributes=True) for m in models]

    async def update_track(self, track_id: int, new_data: NewTrack) -> Track:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(TrackModel).where(TrackModel.id == track_id), session
            )
            if not model:
                raise TrackNotFoundException(track_id)
            updated = await self._update_and_commit(model, new_data, session)
            return Track.model_validate(updated, from_attributes=True)

    async def delete_track(self, track_id: int) -> None:
        async with self.session_factory() as session:
            query = delete(TrackModel).where(TrackModel.id == track_id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise TrackNotFoundException(track_id)
