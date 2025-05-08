from sqlalchemy import Column, Integer, String

from configs.database import Base


class TrackModel(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    artist_id = Column(Integer, nullable=False)
    album_id = Column(Integer, nullable=False)
    picture_path = Column(String, nullable=True)

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "name": self.name.__str__(),
            "artist_id": self.artist_id.__str__(),
            "album_id": self.album_id.__str__(),
            "picture_path": self.picture_path.__str__(),
        }
