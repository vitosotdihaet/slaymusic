from sqlalchemy.ext.declarative import declarative_base
from configs.database import accounts_engine, music_engine, user_activity_engine


Tracks = declarative_base()
Albums = declarative_base()
Artists = declarative_base()


def create_tables():
    Tracks.metadata.create_all(bind=accounts_engine)
    Albums.metadata.create_all(bind=music_engine)
    Artists.metadata.create_all(bind=user_activity_engine)
