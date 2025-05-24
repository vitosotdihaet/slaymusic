from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP, func, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
import datetime

from models.base_model import MusicModelBase


class PlaylistModel(MusicModelBase):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
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

    author: Mapped["UserModel"] = relationship("UserModel", back_populates="playlists")  # noqa: F821 # type: ignore
    tracks: Mapped[list["TrackModel"]] = relationship(  # noqa: F821 # type: ignore
        "TrackModel",
        secondary="playlist_tracks",
        back_populates="playlists",
        cascade="save-update, merge",
    )

    __table_args__ = (
        Index(
            "idx_playlist_name_gin_trgm",
            name,
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    def __repr__(self):
        return (
            f"<Playlist(id={self.id}, name='{self.name}', author_id={self.author_id})>"
        )
