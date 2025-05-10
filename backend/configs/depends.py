from configs.environment import settings
from services.music import MusicService
from repositories.music_file import MinioMusicFileRepository
from repositories.track import SQLAlchemyTrackRepository
from repositories.album import SQLAlchemyAlbumRepository
from repositories.artist import SQLAlchemyArtistRepository
from .database import get_session_generator

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
    app.state.track_repository = await SQLAlchemyTrackRepository.create(
        await get_session_generator("music")
    )
    app.state.album_repository = await SQLAlchemyAlbumRepository.create(
        await get_session_generator("music")
    )
    app.state.artist_repository = await SQLAlchemyArtistRepository.create(
        await get_session_generator("music")
    )

    app.state.music_service = MusicService(
        app.state.music_file_repository,
        app.state.track_repository,
        app.state.album_repository,
        app.state.artist_repository,
    )
    yield


def get_music_service(request: Request) -> MusicService:
    return request.app.state.music_service
