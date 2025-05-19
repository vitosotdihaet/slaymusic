from typing import Optional

from sqlalchemy import delete, func, select, cast, Date
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from exceptions.user_activity import (
    EventNotFoundException,
    UserActivityNotFoundException,
)
from configs.database import ensure_tables
from models.base_model import UserActivityBase
from models.user_activity import EventModel, UserActivityModel
from models.user_activity import add_initial_events
from repositories.helpers import RepositoryHelpers
from repositories.interfaces import IUserActivityRepository
from dto.user_activity import (
    ActiveUsers,
    ActiveUsersOnDate,
    TrackCompletionRate,
    TrackPlayedCount,
    TracksCompletionRate,
    UserActivity,
    MostPlayedTracks,
    UserActivityFilter,
    UserActivityPost,
)


class SQLAlchemyUserActivityRepository(IUserActivityRepository, RepositoryHelpers):
    session: AsyncSession

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @staticmethod
    async def create(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> "SQLAlchemyUserActivityRepository":
        await ensure_tables(UserActivityBase, "user-activity")
        async with session_factory() as session:
            await add_initial_events(session)

        return SQLAlchemyUserActivityRepository(session_factory)

    async def add(self, user_activity: UserActivityPost) -> UserActivity:
        async with self.session_factory() as session:
            event_id = await session.scalar(
                select(EventModel.id).where(EventModel.name == user_activity.event)
            )

            if not event_id:
                raise EventNotFoundException(f"{user_activity.event}")

            db_model = UserActivityModel(
                user_id=user_activity.user_id,
                track_id=user_activity.track_id,
                event_type_id=event_id,
            )

            session.add(db_model)
            await session.commit()
            await session.refresh(db_model, ["event"])

            return UserActivity.model_validate(
                {**db_model.__dict__, "event": db_model.event.name}
            )

    async def get(self, id: int) -> UserActivity:
        async with self.session_factory() as session:
            db_model = (
                await session.execute(
                    select(UserActivityModel)
                    .where(UserActivityModel.id == id)
                    .options(selectinload(UserActivityModel.event))
                )
            ).scalar_one_or_none()

            if not db_model:
                raise UserActivityNotFoundException(f"{id}")

            return UserActivity.model_validate(
                {**db_model.__dict__, "event": db_model.event.name}
            )

    async def list(
        self,
        filter: UserActivityFilter,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> list[UserActivity]:
        async with self.session_factory() as session:
            query = select(UserActivityModel).options(
                selectinload(UserActivityModel.event)
            )

            if filter.ids:
                query = query.where(UserActivityModel.id.in_(filter.ids))
            if filter.user_ids:
                query = query.where(UserActivityModel.user_id.in_(filter.user_ids))
            if filter.track_ids:
                query = query.where(UserActivityModel.track_id.in_(filter.track_ids))
            if filter.events:
                query = query.join(EventModel).filter(
                    EventModel.name.in_(filter.events)
                )
            if filter.start_time:
                query = query.where(UserActivityModel.time >= filter.start_time)
            if filter.end_time:
                query = query.where(UserActivityModel.time <= filter.end_time)

            query = query.offset(offset)
            query = query.limit(limit)

            result = await session.execute(query)
            return [
                UserActivity.model_validate(
                    {**db_model.__dict__, "event": db_model.event.name}
                )
                for db_model in result.scalars().all()
            ]

    async def delete(self, filter: UserActivityFilter) -> None:
        async with self.session_factory() as session:
            query = delete(UserActivityModel)

            if filter.ids:
                query = query.where(UserActivityModel.id.in_(filter.ids))
            if filter.user_ids:
                query = query.where(UserActivityModel.user_id.in_(filter.user_ids))
            if filter.track_ids:
                query = query.where(UserActivityModel.track_id.in_(filter.track_ids))
            if filter.events:
                event_subq = select(EventModel.id).where(
                    EventModel.name.in_(filter.events)
                )
                query = query.where(UserActivityModel.event_type_id.in_(event_subq))
            if filter.start_time:
                query = query.where(UserActivityModel.time >= filter.start_time)
            if filter.end_time:
                query = query.where(UserActivityModel.time <= filter.end_time)

            result = await session.execute(query)
            if result.rowcount == 0:
                raise UserActivityNotFoundException(f"{filter}")
            await session.commit()

    async def get_most_played_tracks(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> MostPlayedTracks:
        async with self.session_factory() as session:
            play_count_label = func.count().label("play_count")
            query = (
                select(UserActivityModel.track_id, play_count_label)
                .join(EventModel)
                .where(EventModel.name == "play")
                .group_by(UserActivityModel.track_id)
                .order_by(play_count_label.desc())
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(query)
            return MostPlayedTracks.model_validate(
                {
                    "tracks": [
                        TrackPlayedCount.model_validate(row) for row in result.all()
                    ]
                }
            )

    async def get_daily_active_users_count(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> ActiveUsers:
        async with self.session_factory() as session:
            query = (
                select(
                    cast(UserActivityModel.time, Date).label("date"),
                    func.count(func.distinct(UserActivityModel.user_id)).label(
                        "user_count"
                    ),
                )
                .group_by("date")
                .order_by("date")
                .offset(offset)
                .limit(limit)
            )
            result = await session.execute(query)
            return ActiveUsers.model_validate(
                {
                    "entries": [
                        ActiveUsersOnDate.model_validate(row) for row in result.all()
                    ]
                }
            )

    async def get_tracks_completion_rate(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> TracksCompletionRate:
        async with self.session_factory() as session:
            play_query = (
                select(UserActivityModel.track_id, func.count().label("plays"))
                .join(EventModel)
                .where(EventModel.name == "play")
                .group_by(UserActivityModel.track_id)
                .cte("plays")
            )

            skip_query = (
                select(UserActivityModel.track_id, func.count().label("skips"))
                .join(EventModel)
                .where(EventModel.name == "skip")
                .group_by(UserActivityModel.track_id)
                .cte("skips")
            )

            query = (
                select(
                    play_query.c.track_id,
                    (skip_query.c.skips / play_query.c.plays).label("completion_rate"),
                )
                .join(skip_query, skip_query.c.track_id == play_query.c.track_id)
                .offset(offset)
                .limit(limit)
            )

            result = await session.execute(query)
            return TracksCompletionRate.model_validate(
                {
                    "entries": [
                        TrackCompletionRate.model_validate(row) for row in result.all()
                    ]
                }
            )