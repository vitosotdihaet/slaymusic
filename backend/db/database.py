import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from fastapi import HTTPException

@contextmanager
def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(
        dbname=os.getenv("POSTGRESQL_ACCOUNTS_DB"),
        user=os.getenv("POSTGRESQL_ACCOUNTS_ROOT_USER"),
        password=os.getenv("POSTGRESQL_ACCOUNTS_ROOT_PASSWORD"),
        host="postgres-accounts-service",
        port=os.getenv("POSTGRESQL_ACCOUNTS_PORT"),
        cursor_factory=RealDictCursor
        )
        print("Database connection established")
        yield conn
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"Can't establish connection to database: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection is closed")