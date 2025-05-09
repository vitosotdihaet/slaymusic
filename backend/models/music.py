from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey

MusicBase = declarative_base()

class ArtistModel(MusicBase):
    __tablename__ = "artists"
    artist_id = Column(Integer, primary_key=True, autoincrement=True)
    artist_name = Column(String, nullable=False)
    artist_picture_path = Column(String, nullable=True)

    def normalize(self):
        return {
            "artist_id": self.artist_id.__str__(),
            "artist_name": self.artist_name.__str__(),
            "artist_picture_path": self.artist_picture_path.__str__(),
        }


class AlbumModel(MusicBase):
    __tablename__ = "albums"
    album_id = Column(Integer, primary_key=True, autoincrement=True)
    artist_id = Column(Integer, ForeignKey("artists.artist_id", ondelete="CASCADE"), nullable=False)
    album_name = Column(String, nullable=False)
    picture_path = Column(String, nullable=True)

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "artist_id": self.artist_id.__str__(),
            "name": self.name.__str__(),
            "picture_path": self.picture_path.__str__(),
        }


class TrackModel(MusicBase):
    __tablename__ = "tracks"
    track_id = Column(Integer, primary_key=True, autoincrement=True)
    track_name = Column(String, nullable=False)
    artist_id = Column(Integer, ForeignKey("artists.artist_id", ondelete="CASCADE") ,nullable=False)
    album_id = Column(Integer, ForeignKey("albums.album_id", ondelete="CASCADE"), nullable=False)
    picture_path = Column(String, nullable=True)

    def normalize(self):
        return {
            "id": self.id.__str__(),
            "name": self.name.__str__(),
            "artist_id": self.artist_id.__str__(),
            "album_id": self.album_id.__str__(),
            "picture_path": self.picture_path.__str__(),
        }
