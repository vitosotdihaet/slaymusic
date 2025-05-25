from sqlalchemy import Enum, Integer, String, Text, Index, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum
import datetime

from models.base_model import MusicModelBase


class UserRoleEnum(enum.Enum):
    user = "user"
    admin = "admin"
    analyst = "analyst"


class UserModel(MusicModelBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    playlists: Mapped[list["PlaylistModel"]] = relationship(  # noqa: F821 # type: ignore
        "PlaylistModel",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    albums: Mapped[list["AlbumModel"]] = relationship(  # noqa: F821 # type: ignore
        "AlbumModel",
        back_populates="artist",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tracks: Mapped[list["TrackModel"]] = relationship(  # noqa: F821 # type: ignore
        "TrackModel",
        back_populates="artist",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    subscriptions: Mapped[list["SubscriptionModel"]] = relationship(  # noqa: F821 # type: ignore
        "SubscriptionModel",
        foreign_keys="SubscriptionModel.subscriber_id",
        back_populates="subscriber",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    subscribers: Mapped[list["SubscriptionModel"]] = relationship(  # noqa: F821 # type: ignore
        "SubscriptionModel",
        foreign_keys="SubscriptionModel.artist_id",
        back_populates="artist",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "idx_artist_name_gin_trgm",
            name,
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', role='{self.role.value}')>"
