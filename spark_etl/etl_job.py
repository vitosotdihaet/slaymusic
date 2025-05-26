from etl_spark.database import get_mongo_url, get_db_creds
from pyspark.sql import SparkSession
from etl_spark.config import *
from pyspark.sql.functions import col, count, sum as spark_sum, to_timestamp, lit
from datetime import datetime, timedelta

yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
driver = "org.postgresql.Driver"
spark = SparkSession.builder \
        .appName("ETL_Mongo_Spark") \
        .config("spark.mongodb.read.connection.uri", get_mongo_url(DB_SOURCE_MONGO)) \
        .config("spark.mongodb.write.connection.uri", get_mongo_url(DB_TARGET_MONGO)) \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1,org.postgresql:postgresql:42.6.0") \
        .getOrCreate()

activity_df = spark.read.format("mongodb") \
        .option("database", DB_SOURCE_MONGO) \
        .option("collection", COLLECTION_ACTIVITY) \
        .load() \
        .filter(col("timestamp") >= to_timestamp(lit(yesterday)))

def read_users(spark):
        creds = get_db_creds("users")
        postgresql_users_url = get_db_creds("users")
        return(spark.read.format("jdbc")
                .option("url", postgresql_users_url)
                .option("dbtable", "users")
                .option("user",    creds["user"])
                .option("password",creds["password"])
                .option("driver",  driver)
                .load())

def read_tracks(spark):
        creds_tracks = get_db_creds("music")
        postgresql_users_url = get_db_creds("music")
        return (spark.read.format("jdbc")
                .option("url", postgresql_users_url)
                .option("dbtable", "tracks")
                .option("user",    creds_tracks["user"])
                .option("password", creds_tracks["password"])
                .option("driver",  driver)
                .load())

def read_genres(spark):
        creds_tracks = get_db_creds("music")
        postgresql_users_url = get_db_creds("music")
        return (spark.read.format("jdbc")
                .option("url", postgresql_users_url)
                .option("dbtable", "tracks")
                .option("user", creds_tracks["user"])
                .option("password", creds_tracks["password"])
                .option("driver", driver)
                .load())

users_df = read_users(spark)
tracks_df = read_tracks(spark)
genres_df = read_genres(spark)

activity_users_df = activity_df.join(users_df, on="user_id", how="left")
activity_tracks_users_df = activity_users_df.join(tracks_df, on="track_id", how="left")
enriched_df = activity_tracks_users_df.join(genres_df, on="genre_id", how="left")
enriched_df.write.format("mongodb")\
        .mode("overwrite") \
        .option("database", DB_TARGET_MONGO) \
        .option("collection", COLLECTION_RESULT) \
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
        .option("database", DB_TARGET_MONGO) \
        .option("collection", "top_played_tracks") \
        .save()

top_skipped = (
        activity_df.filter(col("event") == "skip")
        .groupBy("track_id")
        .agg(count("*").alias("skip_count"))
        .orderBy(col("skip_count").desc())
)

top_skipped.write \
        .format("mongodb") \
        .mode("overwrite") \
        .option("database", DB_TARGET_MONGO) \
        .option("collection", "top_skipped_tracks") \
        .save()
