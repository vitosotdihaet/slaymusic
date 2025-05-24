from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends,
)

from dto.music import TrackID
from exceptions.track_queue import TrackQueueNotFoundException
from services.track_queue import TrackQueueService
from configs.depends import check_access, get_track_queue_service
from dto.accounts import UserMiddleware
from dto.track_queue import (
    InQueueID,
    QueueParameters,
    QueueSrcDestIDs,
    TrackInQueueIDs,
    TrackQueue,
)

router = APIRouter(prefix="/track_queue", tags=["music"])


@router.post(
    "/left",
    status_code=status.HTTP_200_OK,
    description="add a track to the front of a queue (aka play next)",
)
async def track_queue_push_left(
    track_id: TrackID = Depends(TrackID),
    user: UserMiddleware = Depends(check_access),
    user_activity_service: TrackQueueService = Depends(get_track_queue_service),
) -> None:
    try:
        return await user_activity_service.push_left(user.id, track_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


@router.post(
    "/right",
    status_code=status.HTTP_200_OK,
    description="add a track to the end of a queue",
)
async def track_queue_push_right(
    track_id: TrackID = Depends(TrackID),
    user: UserMiddleware = Depends(check_access),
    user_activity_service: TrackQueueService = Depends(get_track_queue_service),
) -> None:
    try:
        return await user_activity_service.push_right(user.id, track_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


@router.get(
    "/",
    response_model=TrackQueue,
    status_code=status.HTTP_200_OK,
    description="list a queue",
)
async def track_queue_list(
    params: QueueParameters = Depends(QueueParameters),
    user: UserMiddleware = Depends(check_access),
    user_activity_service: TrackQueueService = Depends(get_track_queue_service),
) -> TrackQueue:
    try:
        return await user_activity_service.list(user.id, params)
    except TrackQueueNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


@router.delete(
    "/",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="delete the queue",
)
async def track_queue_delete(
    user: UserMiddleware = Depends(check_access),
    user_activity_service: TrackQueueService = Depends(get_track_queue_service),
) -> None:
    try:
        return await user_activity_service.delete(user.id)
    except TrackQueueNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


@router.patch(
    "/insert",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="insert a track before position with index = `queue_id`",
)
async def insert_into_queue(
    ids: TrackInQueueIDs = Depends(TrackInQueueIDs),
    user: UserMiddleware = Depends(check_access),
    user_activity_service: TrackQueueService = Depends(get_track_queue_service),
) -> None:
    try:
        return await user_activity_service.insert(user.id, ids)
    except TrackQueueNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


@router.patch(
    "/move",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="move a track from a position with index = `src_queue_id` to a position with index = `dest_queue_id`",
)
async def move_in_queue(
    ids: QueueSrcDestIDs = Depends(QueueSrcDestIDs),
    user: UserMiddleware = Depends(check_access),
    user_activity_service: TrackQueueService = Depends(get_track_queue_service),
) -> None:
    try:
        return await user_activity_service.move(user.id, ids)
    except TrackQueueNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


@router.patch(
    "/remove",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="remove a track from a position with index = `id`",
)
async def remove_from_queue(
    id: InQueueID = Depends(InQueueID),
    user: UserMiddleware = Depends(check_access),
    user_activity_service: TrackQueueService = Depends(get_track_queue_service),
) -> None:
    try:
        return await user_activity_service.remove(user.id, id)
    except TrackQueueNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )
