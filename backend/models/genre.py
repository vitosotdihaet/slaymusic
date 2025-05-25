from sqlalchemy import Integer, String, Index, TIMESTAMP, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
import datetime

from models.base_model import MusicModelBase


class GenreModel(MusicModelBase):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now()
    )

    tracks: Mapped[list["TrackModel"]] = relationship(  # noqa: F821 # type: ignore
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
