from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from models.base_model import MusicModelBase


class PlaylistTrackModel(MusicModelBase):
    __tablename__ = "playlist_tracks"

    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlists.id", ondelete="CASCADE"), primary_key=True
    )
    track_id: Mapped[int] = mapped_column(
        ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True
    )

    def __repr__(self):
        return (
            f"<PlaylistTrack(playlist_id={self.playlist_id}, track_id={self.track_id})>"
        )
