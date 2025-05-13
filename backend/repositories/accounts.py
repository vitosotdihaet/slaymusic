from dto.accounts import User, NewUser, UserID, NewRoleUser, UserUsername, LoginUserWithID
from repositories.interfaces import IUserRepository
from repositories.helpers import RepositoryHelpers
from models.accounts import UserModel
from models.base_model import AccountsModelBase
from configs.database import ensure_tables
from exceptions.accounts import UserNotFoundException

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select, delete


class SQLAlchemyUserRepository(IUserRepository, RepositoryHelpers):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    @staticmethod
    async def create(
        session_factory: async_sessionmaker[AsyncSession],
    ) -> "SQLAlchemyUserRepository":
        await ensure_tables(AccountsModelBase, "accounts")
        return SQLAlchemyUserRepository(session_factory)

    async def create_user(self, new_user: NewRoleUser) -> User:
        async with self.session_factory() as session:
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

    async def get_user_by_username(self, user: UserUsername) -> LoginUserWithID:
        async with self.session_factory() as session:
            model = await self._get_one_or_none(
                select(UserModel).where(UserModel.username == user.username), session
            )
            if not model:
                raise UserNotFoundException(f"User '{user.username}' not found")
            return LoginUserWithID.model_validate(model, from_attributes=True)

    async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        async with self.session_factory() as session:
            query = select(UserModel).offset(skip).limit(limit)
            models = await self._get_all(query, session)
            return [User.model_validate(m, from_attributes=True) for m in models]

    async def update_user(self, new_user: User) -> User:
        async with self.session_factory() as session:
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
