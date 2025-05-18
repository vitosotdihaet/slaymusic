from configs.environment import settings
from services.music import MusicService
from services.user_activity import UserActivityService
from repositories.music_file import MinioMusicFileRepository
from repositories.track import SQLAlchemyTrackRepository
from repositories.album import SQLAlchemyAlbumRepository
from repositories.artist import SQLAlchemyArtistRepository
from repositories.genre import SQLAlchemyGenreRepository
from repositories.user_activity import SQLAlchemyUserActivityRepository
from configs.database import get_session_generator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.user_activity_repository = await SQLAlchemyUserActivityRepository.create(
        await get_session_generator("user-activity")
    )
    app.state.user_activity_service = UserActivityService(
        app.state.user_activity_repository
    )

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
    app.state.genre_repository = await SQLAlchemyGenreRepository.create(
        await get_session_generator("music")
    )

    app.state.music_service = MusicService(
        app.state.music_file_repository,
        app.state.track_repository,
        app.state.album_repository,
        app.state.artist_repository,
        app.state.genre_repository,
    )
    yield


def get_user_activity_service(request: Request) -> UserActivityService:
    return request.app.state.user_activity_service


def get_music_service(request: Request) -> MusicService:
    return request.app.state.music_service
