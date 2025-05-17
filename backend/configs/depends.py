from configs.environment import settings
from services.music import MusicService
from services.user_activity import UserActivityService
from repositories.music_file import MinioMusicFileRepository
from repositories.track import SQLAlchemyTrackRepository
from repositories.album import SQLAlchemyAlbumRepository
from repositories.artist import SQLAlchemyArtistRepository
from repositories.genre import SQLAlchemyGenreRepository
from services.accounts import AccountService
from repositories.user_activity import SQLAlchemyUserActivityRepository
from repositories.accounts import SQLAlchemyUserRepository
from configs.database import get_session_generator
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dto.accounts import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.user_activity_repository = await SQLAlchemyUserActivityRepository.create(
        await get_session_generator("user-activity")
    )
    app.state.user_activity_service = UserActivityService(
        app.state.user_activity_repository
    )

    app.state.accounts_repository = await SQLAlchemyUserRepository.create(
        await get_session_generator("accounts")
    )

    app.state.accounts_service = AccountService(app.state.accounts_repository)

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


def get_accounts_service(request: Request) -> AccountService:
    return request.app.state.accounts_service


def get_music_service(request: Request) -> MusicService:
    return request.app.state.music_service

security = HTTPBearer()


# можно юзать как мидлварю для аутентификации пользователей
# позже можно сделать отдельно для admin/analyst/user
def check_access(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    account_service: AccountService = Depends(get_accounts_service),
) -> User:
    token = credentials.credentials
    payload = account_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

