from models.base_model import AccountsModelBase as AccountsModelBase
from sqlalchemy import Enum, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum
import datetime


class UserRoleEnum(enum.Enum):
    user = "user"
    admin = "admin"
    analyst = "analyst"


class UserModel(AccountsModelBase):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    playlists: Mapped[list["PlaylistModel"]] = relationship(
        "PlaylistModel", back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', role='{self.role.value}')>"


class PlaylistModel(AccountsModelBase):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "playlists"

    playlist_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    author: Mapped["UserModel"] = relationship("UserModel", back_populates="playlists")
    tracks: Mapped[list["PlaylistTrackModel"]] = relationship(
        "PlaylistTrackModel", back_populates="playlist", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Playlist(id={self.playlist_id}, name='{self.name}', author_id={self.author_id})>"


class PlaylistTrackModel(AccountsModelBase):
    __table_args__ = {"extend_existing": True}
    __tablename__ = "playlist_tracks"

    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlists.playlist_id", ondelete="CASCADE"), primary_key=True
    )
    track_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    playlist: Mapped["PlaylistModel"] = relationship(
        "PlaylistModel", back_populates="tracks"
    )

    def __repr__(self):
        return (
            f"<PlaylistTrack(playlist_id={self.playlist_id}, track_id={self.track_id})>"
        )
