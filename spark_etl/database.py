from etl_spark.environment import settings

def get_db_creds(db_name: str) -> dict[str, str]:
    DB_NAME = db_name.upper().replace("-", "_")
    return {
        "user": getattr(settings, f"{DB_NAME}_ROOT_USER"),
        "password": getattr(settings, f"{DB_NAME}_ROOT_PASSWORD"),
        "port": getattr(settings, f"{DB_NAME}_PORT"),
        "db": getattr(settings, f"{DB_NAME}_DB"),
    }

def get_mongo_url(db_name: str) -> str:
    creds = get_db_creds(db_name)
    host = f"mongodb-{db_name}-service"
    return f"mongodb://{creds['user']}:{creds['password']}@{host}:{creds['port']}?authSource=admin"

def get_psql_url(db_name: str) -> str:
    creds = get_db_creds(db_name)
    host = f"postgres-{db_name}-service"
    return f"jdbc://{creds['user']}:{creds['password']}@{host}:{creds['port']}/{creds['db']}"
