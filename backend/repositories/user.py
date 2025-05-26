from dto.accounts import (
    User,
    UserID,
    NewRoleUser,
    UserUsername,
    FullUser,
    UserSearchParams,
    SubscribersCount,
    Subscribe,
    UpdateUserRole,
    SubscribeSearchParams,
)
from repositories.interfaces import IUserRepository
from repositories.helpers import RepositoryHelpers
from models.user import UserModel
from models.subscription import SubscriptionModel
from exceptions.accounts import (
    UserNotFoundException,
    SubscriptionNotFoundException,
    UserAlreadyExist,
    SubscriptionAlreadyExist,
)

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete, func


class SQLAlchemyUserRepository(IUserRepository, RepositoryHelpers):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def create_user(self, new_user: NewRoleUser) -> User:
        async with self.session_factory() as session:
            query = select(UserModel).where(UserModel.username == new_user.username)
            model = await self._get_one_or_none(query, session)
            if model:
                raise UserAlreadyExist(f"User '{new_user.username}' already exists")
            to_add = UserModel(**new_user.model_dump())
            added = await self._add_and_commit(to_add, session)
            return User.model_validate(added, from_attributes=True)

    async def get_user_by_id(self, user: UserID) -> User:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == user.id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{user.id}' not found")
            return User.model_validate(model, from_attributes=True)

    async def get_user_by_username(self, user: UserUsername) -> FullUser:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.username == user.username), session
            )
            if not model:
                raise UserNotFoundException(f"User '{user.username}' not found")
            return FullUser.model_validate(model, from_attributes=True)

    async def get_users(self, params: UserSearchParams) -> list[User]:
        async with self.session_factory() as session:
            query = select(UserModel)

            if params.name:
                query = query.filter(
                    func.similarity(UserModel.name, params.name) >= params.threshold
                ).order_by(func.similarity(UserModel.name, params.name).desc())

            if params.username:
                query = query.filter(
                    func.similarity(UserModel.username, params.username)
                    >= params.threshold
                ).order_by(func.similarity(UserModel.username, params.username).desc())

            if params.created_search_start:
                query = query.where(UserModel.created_at >= params.created_search_start)

            if params.created_search_end:
                query = query.where(UserModel.created_at <= params.created_search_end)

            if params.updated_search_start:
                query = query.where(UserModel.updated_at >= params.updated_search_start)

            if params.updated_search_end:
                query = query.where(UserModel.updated_at <= params.updated_search_end)

            query = query.offset(params.skip).limit(params.limit)
            models = await self._get_all(query, session)
            return [User.model_validate(m, from_attributes=True) for m in models]

    async def update_user(self, new_user: UpdateUserRole) -> User:
        async with self.session_factory() as session:
            if new_user.username:
                query = select(UserModel).where(UserModel.username == new_user.username)
                model = await self._get_one_or_none(query, session)
                if model:
                    raise UserAlreadyExist(f"User '{new_user.username}' already exists")
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == new_user.id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{new_user.id}' not found")
            updated = await self._update_and_commit(model, new_user, session)
            return User.model_validate(updated, from_attributes=True)

    async def delete_user(self, user: UserID) -> None:
        async with self.session_factory() as session:
            query = delete(UserModel).where(UserModel.id == user.id)
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise UserNotFoundException(f"User '{user.id}' not found")

    async def subscribe_to(self, subscribe: Subscribe) -> None:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == subscribe.subscriber_id),
                session,
            )
            if not model:
                raise UserNotFoundException(
                    f"User '{subscribe.subscriber_id}' not found"
                )
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == subscribe.artist_id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{subscribe.artist_id}' not found")

            model = await self._get_one_or_none(
                select(SubscriptionModel).where(
                    SubscriptionModel.subscriber_id == subscribe.subscriber_id,
                    SubscriptionModel.artist_id == subscribe.artist_id,
                ),
                session,
            )
            if model:
                raise SubscriptionAlreadyExist(
                    f"Subscription from '{subscribe.subscriber_id}' to '{subscribe.artist_id}' already exists"
                )

            sub = SubscriptionModel(**subscribe.model_dump())
            await self._add_and_commit(sub, session)

    async def unsubscribe_from(self, subscribe: Subscribe) -> None:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == subscribe.subscriber_id),
                session,
            )
            if not model:
                raise UserNotFoundException(
                    f"User '{subscribe.subscriber_id}' not found"
                )
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == subscribe.artist_id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{subscribe.artist_id}' not found")

            query = delete(SubscriptionModel).where(
                SubscriptionModel.subscriber_id == subscribe.subscriber_id,
                SubscriptionModel.artist_id == subscribe.artist_id,
            )
            deleted = await self._delete_and_commit(query, session)
            if deleted == 0:
                raise SubscriptionNotFoundException(
                    f"Subscription from '{subscribe.subscriber_id}' to '{subscribe.artist_id}' not found"
                )

    async def get_subscriptions(self, params: SubscribeSearchParams) -> list[User]:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == params.id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{params.id}' not found")

            query = (
                select(UserModel)
                .join(SubscriptionModel, SubscriptionModel.artist_id == UserModel.id)
                .where(SubscriptionModel.subscriber_id == params.id)
            )
            query = query.offset(params.skip).limit(params.limit)
            models = await self._get_all(query, session)
            return [User.model_validate(m, from_attributes=True) for m in models]

    async def get_subscribers(self, params: SubscribeSearchParams) -> list[User]:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == params.id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{params.id}' not found")

            query = (
                select(UserModel)
                .join(
                    SubscriptionModel, SubscriptionModel.subscriber_id == UserModel.id
                )
                .where(SubscriptionModel.artist_id == params.id)
            )
            query = query.offset(params.skip).limit(params.limit)
            models = await self._get_all(query, session)
            return [User.model_validate(m, from_attributes=True) for m in models]

    async def get_subscribe_count(self, user: UserID) -> SubscribersCount:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.id == user.id), session
            )
            if not model:
                raise UserNotFoundException(f"User '{user.id}' not found")

            result = await session.execute(
                select(func.count())
                .select_from(SubscriptionModel)
                .where(SubscriptionModel.artist_id == user.id)
            )
            count = result.scalar_one()
            return SubscribersCount(count=count)
