from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from configs.environment import get_environment_variables


ENV = get_environment_variables()


def get_psql_url(db_name: str) -> str:
    DB_NAME = db_name.upper().replace("-", "_")
    user = getattr(ENV, f'POSTGRESQL_{DB_NAME}_ROOT_USER')
    password = getattr(ENV, f'POSTGRESQL_{DB_NAME}_ROOT_PASSWORD')
    host = f'postgres-{db_name}-service'
    port = getattr(ENV, f'POSTGRESQL_{DB_NAME}_PORT')
    db = getattr(ENV, f'POSTGRESQL_{DB_NAME}_DB')

    return f'postgresql://{user}:{password}@{host}:{port}/{db}'


accounts_engine = create_engine(get_psql_url('accounts'), future=True)
user_activity_engine = create_engine(
    get_psql_url('user-activity'), future=True)
music_engine = create_engine(get_psql_url('music'), future=True)

db_sessions = {
    'accounts': sessionmaker(
        autocommit=False, autoflush=False, bind=accounts_engine),
    'user-activity': sessionmaker(
        autocommit=False, autoflush=False, bind=user_activity_engine),
    'music': sessionmaker(
        autocommit=False, autoflush=False, bind=music_engine)
}


def get_db_connection(db_name: str):
    db = scoped_session(db_sessions[db_name])

    try:
        yield db
    finally:
        db.close()


def get_db_connection_accounts(): return get_db_connection('accounts')
def get_db_connection_user_activity(): return get_db_connection('user-activity')
def get_db_connection_music(): return get_db_connection('music')
