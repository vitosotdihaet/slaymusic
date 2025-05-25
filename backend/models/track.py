from sqlalchemy import Integer, String, ForeignKey, Index, Date, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import datetime

from models.base_model import MusicModelBase


class TrackModel(MusicModelBase):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    album_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("albums.id", ondelete="CASCADE"), nullable=False
    )
    artist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    genre_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("genres.id", ondelete="SET NULL"),
        nullable=True,
    )
    release_date: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    album: Mapped["AlbumModel"] = relationship("AlbumModel", back_populates="tracks")  # noqa: F821 # type: ignore
    artist: Mapped["UserModel"] = relationship("UserModel", back_populates="tracks")  # noqa: F821 # type: ignore
    genre: Mapped["GenreModel"] = relationship("GenreModel", back_populates="tracks")  # noqa: F821 # type: ignore

    playlists: Mapped[list["PlaylistModel"]] = relationship(  # noqa: F821 # type: ignore
        "PlaylistModel",
        secondary="playlist_tracks",
        back_populates="tracks",
    )

    __table_args__ = (
        Index(
            "idx_track_name_gin_trgm",
            name,
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    def __repr__(self):
        return f"<Track(id={self.id}, name='{self.name}', album_id={self.album_id}, artist_id={self.artist_id}, genre_id={self.genre_id})>"
