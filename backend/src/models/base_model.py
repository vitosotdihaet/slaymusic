from sqlalchemy.ext.declarative import declarative_base
from configs.database import accounts_engine, music_engine, user_activity_engine


AccountsModelBase = declarative_base()
MusicModelBase = declarative_base()
UserActivityMetaBase = declarative_base()


def create_tables():
    AccountsModelBase.metadata.create_all(bind=accounts_engine)
    MusicModelBase.metadata.create_all(bind=music_engine)
    UserActivityMetaBase.metadata.create_all(bind=user_activity_engine)
