from configs.environment import settings
from services.music import MusicService
from repositories.music_file import MinioMusicFileRepository
from repositories.music_metadata import SQLAlchemyMusicMetadataRepository
from repositories.artist_repo import SQLAlchemyMusicArtistRepository
from .database import get_music_session, sessions

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.music_file_repository = await MinioMusicFileRepository.create(
        "minio-service:" + str(settings.MINIO_PORT),
        settings.MINIO_ROOT_USER,
        settings.MINIO_ROOT_PASSWORD,
        settings.MINIO_MUSIC_BUCKET,
        settings.MINIO_COVER_BUCKET,
    )
    app.state.music_metadata_repository = (
        await SQLAlchemyMusicMetadataRepository.create(get_music_session())
    )

    async with sessions["music"]() as session:
        app.state.artist_repository = (
            await SQLAlchemyMusicArtistRepository.create(session)
        )
    app.state.music_service = MusicService(
        app.state.music_file_repository, app.state.music_metadata_repository, app.state.artist_repository
    )
    yield



def get_music_service(request: Request) -> MusicService:
    return request.app.state.music_service
