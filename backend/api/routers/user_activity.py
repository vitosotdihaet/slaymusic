from typing import Optional
from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
)

from exceptions.user_activity import (
    UserActivityNotFoundException,
)
from dto.user_activity import (
    UserActivity,
    UserActivityFilter,
    UserActivityPost,
)
from services.user_activity import UserActivityService
from configs.depends import get_user_activity_service

router = APIRouter(prefix="/user_activity", tags=["telemetry"])
activity_metrics_router = APIRouter(prefix="/activity-metrics")


@router.get(
    "/{id}",
    response_model=UserActivity,
    status_code=status.HTTP_200_OK,
)
async def get_user_activity(
    id: int,
    user_activity_service: UserActivityService = Depends(get_user_activity_service),
) -> UserActivity:
    try:
        user_activity = await user_activity_service.get(id)
        return user_activity
    except UserActivityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User activity was not found: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


@router.post(
    "/list",
    response_model=list[UserActivity],
    status_code=status.HTTP_200_OK,
)
async def list_user_activities(
    filter: UserActivityFilter = Depends(),
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    user_activity_service: UserActivityService = Depends(get_user_activity_service),
) -> list[UserActivity]:
    try:
        user_activities = await user_activity_service.list(
            filter, offset=offset, limit=limit
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )

    return user_activities


@router.post("/", response_model=UserActivity, status_code=status.HTTP_201_CREATED)
async def add_user_activity(
    user_activity: UserActivityPost = Depends(),
    user_activity_service: UserActivityService = Depends(get_user_activity_service),
) -> UserActivity:
    try:
        return await user_activity_service.add(user_activity)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")


@router.post("/delete", status_code=status.HTTP_200_OK)
async def delete_user_activity(
    filter: UserActivityFilter = Depends(),
    user_activity_service: UserActivityService = Depends(get_user_activity_service),
):
    try:
        await user_activity_service.delete(filter)
    except UserActivityNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User activity with filter {e} was not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


router.include_router(activity_metrics_router)
