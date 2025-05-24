from configs.environment import settings
from configs.database import get_redis_client_generator, get_session_generator
from dto.accounts import UserMiddleware, UserRole
from services.music import MusicService
from services.user_activity import UserActivityService
from services.accounts import AccountService
from services.track_queue import TrackQueueService
from repositories.music_file import MinioMusicFileRepository
from repositories.track import SQLAlchemyTrackRepository
from repositories.album import SQLAlchemyAlbumRepository
from repositories.genre import SQLAlchemyGenreRepository
from repositories.user import SQLAlchemyUserRepository
from repositories.user_activity import MongoDBUserActivityRepository
from repositories.playlist import SQLAlchemyPlaylistRepository
from repositories.track_queue import RedisTrackQueueRepository

from typing import Type, Callable
from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.user_activity_repository = await MongoDBUserActivityRepository.create()
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
    app.state.track_repository = SQLAlchemyTrackRepository(
        await get_session_generator("music")
    )
    app.state.album_repository = SQLAlchemyAlbumRepository(
        await get_session_generator("music")
    )
    app.state.genre_repository = SQLAlchemyGenreRepository(
        await get_session_generator("music")
    )
    app.state.user_repository = SQLAlchemyUserRepository(
        await get_session_generator("music")
    )
    app.state.playlist_repository = SQLAlchemyPlaylistRepository(
        await get_session_generator("music")
    )

    app.state.music_service = MusicService(
        app.state.music_file_repository,
        app.state.track_repository,
        app.state.album_repository,
        app.state.genre_repository,
    )
    app.state.account_service = AccountService(
        app.state.user_repository,
        app.state.playlist_repository,
        app.state.music_file_repository,
        app.state.album_repository,
        app.state.track_repository,
    )
    app.state.track_queue_repository = await RedisTrackQueueRepository.create(
        get_redis_client_generator("track-queue"), settings.TRACK_QUEUE_TTL
    )

    app.state.track_queue_service = TrackQueueService(app.state.track_queue_repository)
    yield


def get_user_activity_service(request: Request) -> UserActivityService:
    return request.app.state.user_activity_service


def get_account_service(request: Request) -> AccountService:
    return request.app.state.account_service


def get_music_service(request: Request) -> MusicService:
    return request.app.state.music_service


def get_track_queue_service(request: Request) -> TrackQueueService:
    return request.app.state.track_queue_service


security = HTTPBearer()


# можно юзать как мидлварю для аутентификации пользователей
# позже можно сделать отдельно для admin/analyst/user
def check_access(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    account_service: AccountService = Depends(get_account_service),
) -> UserMiddleware:
    token = credentials.credentials
    payload = account_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    account_service: AccountService = Depends(get_account_service),
) -> UserMiddleware:
    token = credentials.credentials
    user = account_service.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return user


def require_owner_or_admin(model: Type[BaseModel], field_name: str) -> Callable:
    def dependency(
        body: model = Depends(model),  # type: ignore
        current_user: UserMiddleware = Depends(get_current_user),
    ) -> BaseModel:
        target_id = getattr(body, field_name)
        if current_user.role != UserRole.admin and target_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not allowed to modify resource owned by user {target_id}",
            )
        return current_user

    return dependency


# Example of require_owner_or_admin usage
# @router.post(
#     "/subscribe",
#     status_code=status.HTTP_201_CREATED,
# )
# async def subscribe_to(
#     subscribe: Subscribe = Depends(),
#     user_data: UserMiddleware = Depends(
#         require_owner_or_admin(Subscribe, "subscriber_id")
#     ),
#     account_service: AccountService = Depends(get_account_service),
# ):
#     if subscribe.subscriber_id == subscribe.artist_id:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Cannot subscribe to self"
#         )
#     try:
#         await account_service.subscribe_to(subscribe)
#     except UserNotFoundException as e:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
#     except SubscriptionAlreadyExist as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


def check_admin_access(
    user_data=Depends(check_access),
) -> UserMiddleware:
    if not user_data.role == UserRole.admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user_data
