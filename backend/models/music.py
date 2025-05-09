from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, Mapped, mapped_column

MusicBase = declarative_base()


class ArtistModel(MusicBase):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    albums: Mapped[list["AlbumModel"]] = relationship(
        "AlbumModel", back_populates="artist", cascade="all, delete-orphan"
    )
    tracks: Mapped[list["TrackModel"]] = relationship(
        "TrackModel", back_populates="artist", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Artist(id={self.id}, name='{self.name}')>"


class AlbumModel(MusicBase):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    artist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )

    artist: Mapped["ArtistModel"] = relationship("ArtistModel", back_populates="albums")
    tracks: Mapped[list["TrackModel"]] = relationship(
        "TrackModel", back_populates="album", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Album(id={self.id}, name='{self.name}', artist_id={self.artist_id})>"


class TrackModel(MusicBase):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    album_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("albums.id", ondelete="CASCADE"), nullable=False
    )
    artist_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )

    album: Mapped["AlbumModel"] = relationship("AlbumModel", back_populates="tracks")
    artist: Mapped["ArtistModel"] = relationship("ArtistModel", back_populates="tracks")

    def __repr__(self):
        return f"<Track(id={self.id}, name='{self.name}', album_id={self.album_id}, artist_id={self.artist_id})>"
