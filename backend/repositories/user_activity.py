from typing import Optional

from beanie import PydanticObjectId
from beanie.operators import In

from exceptions.user_activity import (
    UserActivityNotFoundException,
)
from configs.database import init_mongo_db
from models.user_activity import UserActivityModel
from repositories.interfaces import IUserActivityRepository
from dto.user_activity import (
    UserActivity,
    UserActivityFilter,
    UserActivityPost,
)


class MongoDBUserActivityRepository(IUserActivityRepository):
    @staticmethod
    async def create() -> "MongoDBUserActivityRepository":
        await init_mongo_db([UserActivityModel], "user-activity")
        return MongoDBUserActivityRepository()

    async def add(self, user_activity: UserActivityPost) -> UserActivity:
        doc = UserActivityModel(
            user_id=user_activity.user_id,
            track_id=user_activity.track_id,
            event=user_activity.event,
        )
        await doc.insert()
        return UserActivity.model_validate(
            {
                **doc.model_dump(),
                "id": int(str(doc.id), 16),
            }
        )

    async def get(self, id: int) -> UserActivity:
        mongo_id = hex(id)[2:]
        if not PydanticObjectId.is_valid(mongo_id):
            raise UserActivityNotFoundException(id)
        doc = await UserActivityModel.get(PydanticObjectId(mongo_id))
        if not doc:
            raise UserActivityNotFoundException(id)
        return UserActivity.model_validate(
            {
                **doc.model_dump(),
                "id": int(str(doc.id), 16),
            }
        )

    async def list(
        self, filter: UserActivityFilter, offset: Optional[int], limit: Optional[int]
    ) -> list[UserActivity]:
        query = {}

        if filter.ids:
            mongo_ids = [hex(id)[2:] for id in filter.ids]
            if not all([PydanticObjectId.is_valid(id) for id in mongo_ids]):
                raise UserActivityNotFoundException(filter.ids)
            query["_id"] = {"$in": [PydanticObjectId(id) for id in mongo_ids]}
        if filter.user_ids:
            query["user_id"] = {"$in": filter.user_ids}
        if filter.track_ids:
            query["track_id"] = {"$in": filter.track_ids}
        if filter.events:
            query["event"] = {"$in": filter.events}
        if filter.start_time:
            query.setdefault("time", {})["$gte"] = filter.start_time
        if filter.end_time:
            query.setdefault("time", {})["$lte"] = filter.end_time

        cursor = UserActivityModel.find(query)
        if offset:
            cursor = cursor.skip(offset)
        if limit:
            cursor = cursor.limit(limit)

        results = await cursor.to_list()
        activities = []
        for doc in results:
            activities.append(
                UserActivity.model_validate(
                    {
                        **doc.model_dump(),
                        "id": int(str(doc.id), 16),
                    }
                )
            )
        return activities

    async def delete(self, filter: UserActivityFilter) -> None:
        docs = await self.list(filter, offset=None, limit=None)
        if not docs:
            raise UserActivityNotFoundException(str(filter))
        ids = [PydanticObjectId(hex(doc.id)[2:]) for doc in docs]
        await UserActivityModel.find(In(UserActivityModel.id, ids)).delete()
