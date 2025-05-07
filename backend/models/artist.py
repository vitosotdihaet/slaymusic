from sqlalchemy import (
    Column,
    Integer,
    String
)

from models.base_model import Artists


class Artist(Artists):
    __tablename__ = "artist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    picture = Column(String)

    def normalize(self):
        return {
            'id': self.id.__str__(),
            'name': self.name.__str__(),
            'picture': self.picture.__str__(),
        }

