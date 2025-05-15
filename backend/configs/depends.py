from services.user_activity import UserActivityService
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

    yield


def get_user_activity_service(request: Request) -> UserActivityService:
    return request.app.state.user_activity_service
