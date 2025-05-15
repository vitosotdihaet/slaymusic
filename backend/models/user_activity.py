from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

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
        async with session.begin():
            session.add_all(
                [
                    EventModel(name="play"),
                    EventModel(name="skip"),
                    EventModel(name="add to playlist"),
                ]
            )
            await session.commit()
    except Exception as e:
        logger.warning("could not insert initial events: %s", e)
