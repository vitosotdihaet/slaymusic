from sqlalchemy import Integer, String, ForeignKey, Index, Date, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import datetime

from models.base_model import MusicModelBase


class AlbumModel(MusicModelBase):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    artist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    release_date: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    artist = relationship("UserModel", back_populates="albums")
    tracks: Mapped[list["TrackModel"]] = relationship(  # noqa: F821 # type: ignore
        "TrackModel",
        back_populates="album",
        cascade="save-update, merge, delete, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "idx_album_name_gin_trgm",
            name,
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    def __repr__(self):
        return f"<Album(id={self.id}, name='{self.name}', artist_id={self.artist_id})>"
