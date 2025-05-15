from sqlalchemy.ext.asyncio import AsyncSession


class RepositoryHelpers:
    async def _execute_query(self, query, session: AsyncSession):
        result = await session.execute(query)
        return result

    async def _get_one_or_none(self, query, session: AsyncSession):
        result = await session.execute(query)
        return result.scalars().one_or_none()

    async def _get_all(self, query, session: AsyncSession):
        result = await session.execute(query)
        return result.scalars().all()

    async def _add_and_commit(self, instance, session: AsyncSession):
        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def _update_and_commit(self, instance, new_data, session: AsyncSession):
        for field, value in new_data.model_dump().items():
            setattr(instance, field, value)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def _delete_and_commit(self, query, session: AsyncSession) -> int:
        result = await session.execute(query)
        await session.commit()
        return result.rowcount
