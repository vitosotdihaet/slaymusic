from dto.music import TrackID
from repositories.interfaces import ITrackQueueRepository
from dto.track_queue import (
    InQueueID,
    QueueParameters,
    QueueSrcDestIDs,
    TrackInQueueIDs,
    TrackQueue,
)


class TrackQueueService:
    track_queue_repository: ITrackQueueRepository

    def __init__(self, track_queue_repository: ITrackQueueRepository) -> None:
        self.track_queue_repository = track_queue_repository

    async def push_left(self, user_id: int, id: TrackID) -> None:
        return await self.track_queue_repository.push_left(user_id, id)

    async def push_right(self, user_id: int, id: TrackID) -> None:
        return await self.track_queue_repository.push_right(user_id, id)

    async def list(self, user_id: int, params: QueueParameters) -> TrackQueue:
        return await self.track_queue_repository.list(user_id, params)

    async def delete(self, user_id: int) -> None:
        return await self.track_queue_repository.delete(user_id)

    async def insert(self, user_id: int, ids: TrackInQueueIDs):
        return await self.track_queue_repository.insert(user_id, ids)

    async def move(self, user_id: int, ids: QueueSrcDestIDs):
        return await self.track_queue_repository.move(user_id, ids)

    async def remove(self, user_id: int, queue_id: InQueueID) -> None:
        return await self.track_queue_repository.remove(user_id, queue_id)
