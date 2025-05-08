from configs.environment import settings
from services.music import MusicService
from repositories.music_file import MinioMusicFileRepository
from repositories.music_metadata import SQLAlchemyMusicMetadataRepository
from .database import get_async_session

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
    async for session in get_async_session():
        app.state.music_metadata_repository = (
            await SQLAlchemyMusicMetadataRepository.create(session)
        )

    app.state.music_service = MusicService(
        app.state.music_file_repository, app.state.music_metadata_repository
    )
    yield


def get_music_service(request: Request) -> MusicService:
    return request.app.state.music_service
