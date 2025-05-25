from sqlalchemy import ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import datetime

from models.base_model import MusicModelBase


class SubscriptionModel(MusicModelBase):
    __tablename__ = "subscriptions"

    subscriber_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )

    subscriber: Mapped["UserModel"] = relationship(  # noqa: F821 # type: ignore
        "UserModel",
        foreign_keys=[subscriber_id],
        back_populates="subscriptions",
    )
    artist: Mapped["UserModel"] = relationship(  # noqa: F821 # type: ignore
        "UserModel",
        foreign_keys=[artist_id],
        back_populates="subscribers",
    )

    def __repr__(self):
        return f"<Subscription(subscriber_id={self.subscriber_id}, artist_id={self.artist_id})>"
