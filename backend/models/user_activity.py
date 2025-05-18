from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, ForeignKey, select
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from configs.logging import logger
from models.base_model import UserActivityBase


class EventModel(UserActivityBase):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    activities = relationship("UserActivityModel", back_populates="event")


class UserActivityModel(UserActivityBase):
    __tablename__ = "user_activity"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    track_id: Mapped[int] = mapped_column(nullable=False)
    event_type_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    event = relationship("EventModel", back_populates="activities")
    # always calculated on the server
    time: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)


async def add_initial_events(session: AsyncSession):
    try:
        names = ["play", "skip", "add to playlist"]
        async with session.begin():
            existing = (
                (
                    await session.execute(
                        select(EventModel.name).where(EventModel.name.in_(names))
                    )
                )
                .scalars()
                .all()
            )
            to_create = [EventModel(name=n) for n in names if n not in existing]
            session.add_all(to_create)
    except Exception as e:
        logger.warning("could not insert initial events: %s", e)
