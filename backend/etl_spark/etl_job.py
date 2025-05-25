from configs.database import get_mongo_url, get_db_creds
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, to_timestamp, lit
from datetime import datetime, timedelta
yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()

spark = SparkSession.builder \
        .appName("ETL_Mongo_Spark") \
        .config("spark.mongodb.read.connection.uri", get_mongo_url("user_activity")) \
        .config("spark.mongodb.write.connection.uri", get_mongo_url("daily-user_activity")) \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1,org.postgresql:postgresql:42.6.0") \
        .getOrCreate()

activity_df = spark.read.format("mongodb") \
        .option("database", "user_activity") \
        .option("collection", "user-activity") \
        .load() \
        .filter(col("timestamp") >= to_timestamp(lit(yesterday)))
driver = "org.postgresql.Driver"

creds = get_db_creds("users")
host_users = f"postgres-users-service"
postgresql_users_url = f"jdbc:postgresql//{creds['user']}:{creds['password']}@{host}:{creds['port']}/{creds['db']}"
users_df = spark.read.format("jdbc")\
        .option("url", postgresql_users_url) \
        .option("dbtable", "users") \
        .option("user",    creds["user"]) \
        .option("password",creds["password"]) \
        .option("driver",  driver) \
        .load()

creds_tracks = get_db_creds("music")
host_tracks = f"postgres-music-service"
postgresql_users_url = f"jdbc:postgresql//{creds_tracks['user']}:{creds_tracks['password']}@{host_tracks}:{creds_tracks['port']}/{creds_tracks['db']}"
tracks_df = spark.read.format("jdbc")\
        .option("url", postgresql_users_url) \
        .option("dbtable", "tracks") \
        .option("user",    creds_tracks["user"]) \
        .option("password", creds_tracks["password"]) \
        .option("driver",  driver) \
        .load()

genres_df = spark.read.format("jdbc")\
        .option("url", postgresql_users_url) \
        .option("dbtable", "genres") \
        .option("user",    creds_tracks["user"]) \
        .option("password", creds_tracks["password"]) \
        .option("driver",  driver) \
        .load()

activity_users_df = activity_df.join(users_df, on="user_id", how="left")
activity_tracks_users_df = activity_users_df.join(tracks_df, on="track_id", how="left")
enriched_df = activity_tracks_users_df.join(genres_df, on="genre_id", how="left")
enriched_df.write.format("mongodb")\
        .mode("overwrite") \
        .option("database", "daily_user_activity") \
        .option("collection", "enriched_activity") \
        .option("replaceDocument", "true") \
        .save()

top_played = (
        activity_df.groupBy("track_id")
        .agg(count("*").alias("play_count"))
        .orderBy(col("play_count").desc())
)

top_played.write \
        .format("mongodb") \
        .mode("overwrite") \
        .option("database", "daily_user_activity") \
        .option("collection", "top_played_tracks") \
        .save()

top_skipped = (
        activity_df.filter(col("skipped") == True)
        .groupBy("track_id")
        .agg(count("*").alias("skip_count"))
        .orderBy(col("skip_count").desc())
)

top_skipped.write \
        .format("mongodb") \
        .mode("overwrite") \
        .option("database", "daily_user_activity") \
        .option("collection", "top_skipped_tracks") \
        .save()
