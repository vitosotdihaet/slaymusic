import os
import glob
import psycopg2
from psycopg2 import sql
from psycopg2.extras import LoggingConnection
import logging


def get_url(database_name):
    """Generate a URL from the environment variables."""
    ENT = database_name.upper().replace("-", "_")
    return "postgresql://%s:%s@%s:%s/%s" % (
        os.getenv(f"POSTGRESQL_{ENT}_ROOT_USER"),
        os.getenv(f"POSTGRESQL_{ENT}_ROOT_PASSWORD"),
        f"postgres-{database_name}-service",
        os.getenv(f"POSTGRESQL_{ENT}_PORT"),
        os.getenv(f"POSTGRESQL_{ENT}_DB"),
    )

def apply_migration(cursor, sql_file):
    """Apply a single SQL migration file."""
    with open(sql_file, 'r') as file:
        sql_script = file.read()
        try:
            cursor.execute(sql_script)
            logging.info(f"Applied migration: {sql_file}")
        except Exception as e:
            logging.error(f"Failed to apply migration: {sql_file}")
            logging.error(e)
            raise

def apply_migrations(database_name):
    """Apply all SQL migration files in the specified directory."""
    url = get_url(database_name)
    logging.info(f"Connecting to database: {url}")
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(url, connection_factory=LoggingConnection)
        connection.initialize(logging.getLogger())
        connection.autocommit = True
        cursor = connection.cursor()

        directory = f"migrations/{database_name}"
        sql_files = sorted(glob.glob(os.path.join(directory, '*.sql')))
        for sql_file in sql_files:
            apply_migration(cursor, sql_file)

    except Exception as e:
        logging.error(f"Database connection failed: {e}")
    finally:
        if connection:
            if cursor:
                cursor.close()
            connection.close()
            logging.info("Database connection closed")

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    databases = ["accounts", "music", "user-activity"]

    for database in databases:
        apply_migrations(database)
