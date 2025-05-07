from sqlalchemy import (
    Column,
    Integer,
    String
)

from models.base_model import Tracks


class Track(Tracks):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    artist_id = Column(Integer, nullable=False)
    album_id = Column(Integer, nullable=False)

    def normalize(self):
        return {
            'id': self.id.__str__(),
            'name': self.name.__str__(),
            'artist_id': self.artist_id.__str__(),
            'album_id': self.album_id.__str__(),
        }

