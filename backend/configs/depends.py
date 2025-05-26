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
from exceptions.accounts import AccountsBaseException
from exceptions.music import MusicBaseException

from typing import Type, Callable, Any
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
optional_bearer = HTTPBearer(auto_error=False)


def check_access(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    account_service: AccountService = Depends(get_account_service),
) -> UserMiddleware:
    token = credentials.credentials
    payload = account_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return payload


def check_access_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(optional_bearer),
    account_service: AccountService = Depends(get_account_service),
) -> UserMiddleware | None:
    if not credentials or not credentials.credentials:
        return None
    token = credentials.credentials
    payload = account_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return payload


def check_admin_access(
    user_data: UserMiddleware = Depends(check_access),
) -> UserMiddleware:
    if user_data.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return user_data


def get_login_or_user(model: Type[BaseModel], field_name: str) -> Callable:
    def dependency(
        body: model = Depends(model),  # type: ignore
        current_user: UserMiddleware | None = Depends(check_access_optional),
    ) -> BaseModel:
        explicit_id = getattr(body, field_name, None)
        if explicit_id is not None:
            target_id = explicit_id
        elif current_user is not None:
            target_id = current_user.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either set the field or be logged in",
            )
        setattr(body, field_name, target_id)

        return body

    return dependency


def get_login_or_admin(model: Type[BaseModel], field_name: str) -> Callable:
    def dependency(
        body: model = Depends(model),  # type: ignore
        current_user: UserMiddleware = Depends(check_access),
    ) -> BaseModel:
        target_id = getattr(body, field_name, None)
        if target_id is None:
            target_id = current_user.id
        setattr(body, field_name, target_id)

        if current_user.role != UserRole.admin and target_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not allowed to modify resource owned by user {target_id}",
            )
        return body

    return dependency


class ID(BaseModel):
    id: int


def require_owner_or_admin(
    model: Type[BaseModel],
    id_field_name: str,
    get_method_name_in_service: str,
    service_dependency: Callable[..., Any],
) -> Callable:
    async def dep(
        body: model = Depends(model),  # type: ignore
        current_user: UserMiddleware = Depends(check_access),
        service: MusicService = Depends(service_dependency),
    ) -> UserMiddleware:
        body_id = getattr(body, id_field_name, None)
        if body_id is None:
            return current_user

        get_object_method = getattr(service, get_method_name_in_service, None)

        try:
            target_object = await get_object_method(ID(id=body_id))
        except (
            AccountsBaseException,
            MusicBaseException,
        ) as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )

        owner_id = getattr(target_object, "artist_id", None)
        if owner_id is None:
            owner_id = getattr(target_object, "author_id")

        if current_user.role != UserRole.admin and owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not allowed to modify resource owned by user {owner_id}",
            )
        return current_user

    return dep
