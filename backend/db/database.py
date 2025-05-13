# import os
# import psycopg2
# from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# from contextlib import contextmanager
from migrations.apply import get_url

url = get_url("accounts")
engine = create_engine(url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# @contextmanager
def get_db_connection():
    db = SessionLocal()
    try:
        print("Database connection established")
        yield db
    finally:
        db.close()
        print("Database connection is closed")
    
    # conn = None
    # try:
    #     conn = psycopg2.connect(
    #     dbname=os.getenv("POSTGRESQL_ACCOUNTS_DB"),
    #     user=os.getenv("POSTGRESQL_ACCOUNTS_ROOT_USER"),
    #     password=os.getenv("POSTGRESQL_ACCOUNTS_ROOT_PASSWORD"),
    #     host="postgres-accounts-service",
    #     port=os.getenv("POSTGRESQL_ACCOUNTS_PORT"),
    #     cursor_factory=RealDictCursor
    #     )
    #     print("Database connection established")
    #     yield conn
    # except Exception as e:
    #     raise HTTPException (status_code=500, detail=f"Can't establish connection to database: {e}")
    # finally:
    #     if conn:
    #         conn.close()
    #         print("Database connection is closed")

