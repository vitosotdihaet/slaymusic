from typing import Optional

from repositories.interfaces import IUserActivityRepository
from dto.user_activity import (
    ActiveUsers,
    TracksCompletionRate,
    UserActivity,
    MostPlayedTracks,
    UserActivityFilter,
    UserActivityPost,
)


class UserActivityService:
    user_activity_repository: IUserActivityRepository

    def __init__(
        self,
        user_activity_repository: IUserActivityRepository,
    ) -> None:
        self.user_activity_repository = user_activity_repository

    async def add(self, user_activity: UserActivityPost) -> UserActivity:
        return await self.user_activity_repository.add(user_activity)

    async def get(self, id: int) -> UserActivity:
        return await self.user_activity_repository.get(id)

    async def list(
        self,
        filter: UserActivityFilter,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[UserActivity]:
        return await self.user_activity_repository.list(
            filter,
            offset=offset,
            limit=limit,
        )

    async def delete(self, filter: UserActivityFilter) -> None:
        return await self.user_activity_repository.delete(filter)

    async def get_most_played_tracks(
        self, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> MostPlayedTracks:
        return await self.user_activity_repository.get_most_played_tracks(
            offset=offset, limit=limit
        )

    async def get_daily_active_users_count(
        self, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> ActiveUsers:
        return await self.user_activity_repository.get_daily_active_users_count(
            offset=offset, limit=limit
        )

    async def get_tracks_completion_rate(
        self, offset: Optional[int] = None, limit: Optional[int] = None
    ) -> TracksCompletionRate:
        return await self.user_activity_repository.get_tracks_completion_rate(
            offset=offset, limit=limit
        )
