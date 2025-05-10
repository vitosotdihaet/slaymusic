from dto.music import Track, NewTrack, TrackID, AlbumID, ArtistID
from repositories.interfaces import ITrackRepository
from repositories.base_music_metadata import SQLAlchemyBaseMusicMetadataRepository
from models.music import MusicBase, TrackModel, AlbumModel, ArtistModel
from configs.database import ensure_tables
from exceptions.music import (
    AlbumNotFoundException,
    ArtistNotFoundException,
    TrackNotFoundException,
)

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete


class SQLAlchemyTrackRepository(
    ITrackRepository, SQLAlchemyBaseMusicMetadataRepository
):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> "SQLAlchemyTrackRepository":
        await ensure_tables(MusicBase, "music")
        return SQLAlchemyTrackRepository(session_factory)

    async def create_track(self, new_track: NewTrack) -> Track:
        async with self.session_factory() as session:
            album = await self._get_one_or_none(
                select(AlbumModel).where(AlbumModel.id == new_track.album_id), session
            )
            if not album:
                raise AlbumNotFoundException(f"Album '{new_track.album_id}' not found")
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

    async def get_tracks_by_artist(
        self, artist: ArtistID, skip: int = 0, limit: int = 100
    ) -> list[Track]:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(ArtistModel).where(ArtistModel.id == artist.id), session
            )
            if not model:
                raise ArtistNotFoundException(f"Artist '{artist.id}' not found")
            query = (
                select(TrackModel)
                .where(TrackModel.artist_id == artist.id)
                .offset(skip)
                .limit(limit)
            )
            models = await self._get_all(query, session)
            return [Track.model_validate(m, from_attributes=True) for m in models]

    async def get_tracks_by_album(
        self, album: AlbumID, skip: int = 0, limit: int = 100
    ) -> list[Track]:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(AlbumModel).where(AlbumModel.id == album.id), session
            )
            if not model:
                raise AlbumNotFoundException(f"Album '{album.id}' not found")
            query = (
                select(TrackModel)
                .where(TrackModel.album_id == album.id)
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
            model = await self._get_one_or_none(
                select(TrackModel).where(TrackModel.id == new_track.id), session
            )
            if not model:
                raise TrackNotFoundException(f"Track '{new_track.id}' not found")
            updated = await self._update_and_commit(model, new_track, session)
            return Track.model_validate(updated, from_attributes=True)

    async def delete_track(self, track: TrackID) -> None:
        async with self.session_factory() as session:
            query = delete(TrackModel).where(TrackModel.id == track.id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise TrackNotFoundException(f"Track '{track.id}' not found")
