from sqlalchemy import Integer, String, Text, ForeignKey, Index, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column

from models.base_model import MusicModelBase


class ArtistModel(MusicModelBase):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    albums: Mapped[list["AlbumModel"]] = relationship(
        "AlbumModel",
        back_populates="artist",
        cascade="save-update, merge, delete, delete-orphan",
        passive_deletes=True,
    )
    tracks: Mapped[list["TrackModel"]] = relationship(
        "TrackModel",
        back_populates="artist",
        cascade="save-update, merge, delete, delete-orphan",
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
        return f"<Artist(id={self.id}, name='{self.name}')>"


class GenreModel(MusicModelBase):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    tracks: Mapped[list["TrackModel"]] = relationship(
        "TrackModel",
        back_populates="genre",
    )

    __table_args__ = (
        Index(
            "idx_genre_name_gin_trgm",
            name,
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    def __repr__(self):
        return f"<Genre(id={self.id}, name='{self.name}')>"


class AlbumModel(MusicModelBase):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    artist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )

    artist: Mapped["ArtistModel"] = relationship("ArtistModel", back_populates="albums")
    tracks: Mapped[list["TrackModel"]] = relationship(
        "TrackModel",
        back_populates="album",
        cascade="save-update, merge, delete, delete-orphan",
        passive_deletes=True,
    )
    release_date: Mapped[Date] = mapped_column(Date)

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
        Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )
    genre_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("genres.id", ondelete="SET NULL"),
        nullable=True,
    )
    release_date: Mapped[Date] = mapped_column(Date, nullable=False)

    __table_args__ = (
        Index(
            "idx_track_name_gin_trgm",
            name,
            postgresql_using="gin",
            postgresql_ops={"name": "gin_trgm_ops"},
        ),
    )

    album: Mapped["AlbumModel"] = relationship("AlbumModel", back_populates="tracks")
    artist: Mapped["ArtistModel"] = relationship("ArtistModel", back_populates="tracks")
    genre: Mapped["GenreModel"] = relationship("GenreModel", back_populates="tracks")

    def __repr__(self):
        return f"<Track(id={self.id}, name='{self.name}', album_id={self.album_id}, artist_id={self.artist_id}, genre_id={self.genre_id})>"
