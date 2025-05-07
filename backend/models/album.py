from sqlalchemy import (
    Column,
    Integer,
    String
)

from models.base_model import Albums


class Album(Albums):
    __tablename__ = "albums"
    id = Column(Integer, primary_key=True, autoincrement=True)
    artist_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    picture = Column(String)

    def normalize(self):
        return {
            'id': self.id.__str__(),
            'artist_id': self.artist_id.__str__(),
            'name': self.name.__str__(),
            'picture': self.picture.__str__(),
        }

