from sqlalchemy.ext.asyncio import AsyncSession


class RepositoryHelpers:
    @staticmethod
    async def _execute_query(query, session: AsyncSession):
        result = await session.execute(query)
        return result

    @staticmethod
    async def _get_one_or_none(query, session: AsyncSession):
        result = await session.execute(query)
        return result.scalars().one_or_none()

    @staticmethod
    async def _get_all(query, session: AsyncSession):
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def _add_and_commit(instance, session: AsyncSession):
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    @staticmethod
    async def _update_and_commit(instance, new_data, session: AsyncSession):
        for field, value in new_data.model_dump().items():
            setattr(instance, field, value)
        await session.commit()
        await session.refresh(instance)
        return instance

    @staticmethod
    async def _delete_and_commit(query, session: AsyncSession) -> int:
        result = await session.execute(query)
        await session.commit()
        return result.rowcount
