from sqlalchemy import Column, Integer, String

from configs.database import Base


class ArtistModel(Base):
    __tablename__ = "artists"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    picture_path = Column(String, nullable=True)

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "name": self.name.__str__(),
            "picture_path": self.picture_path.__str__(),
        }
