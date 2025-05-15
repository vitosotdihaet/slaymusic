from dto.user_activity import (
    ActiveUsers,
    TracksCompletionRate,
    UserActivity,
    MostPlayedTracks,
    UserActivityFilter,
    UserActivityPost,
)

from typing import Optional, Protocol


class IUserActivityRepository(Protocol):
    async def add(
        self,
        user_activity: UserActivityPost,
    ) -> UserActivity: ...

    async def get(
        self,
        id: int,
    ) -> UserActivity: ...

    async def list(
        self,
        filter: UserActivityFilter,
        offset: Optional[int],
        limit: Optional[int],
    ) -> list[UserActivity]: ...

    async def delete(self, filter: UserActivityFilter) -> None: ...

    async def get_most_played_tracks(
        self,
        offset: Optional[int],
        limit: Optional[int],
    ) -> MostPlayedTracks: ...

    async def get_daily_active_users_count(
        self,
        offset: Optional[int],
        limit: Optional[int],
    ) -> ActiveUsers: ...

    async def get_tracks_completion_rate(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> TracksCompletionRate: ...
