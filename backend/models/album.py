from sqlalchemy import Column, Integer, String

from configs.database import Base


class AlbumModel(Base):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, autoincrement=True)
    artist_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    picture_path = Column(String, nullable=True)

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "artist_id": self.artist_id.__str__(),
            "name": self.name.__str__(),
            "picture_path": self.picture_path.__str__(),
        }
