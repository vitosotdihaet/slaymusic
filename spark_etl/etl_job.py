import pyspark
from spark_etl.database import get_mongo_url, get_db_creds, get_psql_url
from pyspark.sql import SparkSession
from spark_etl.config import *
from pyspark.sql.functions import (
    col, count, to_timestamp, lit, to_date,
    weekofyear, month, when, desc, row_number
)
from pyspark.sql.window import Window
from datetime import datetime, timedelta


yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()

driver = "org.postgresql.Driver"

_creds_music = get_db_creds("music")
_psql_url_music = get_psql_url("music")

spark = (
    SparkSession.builder
    .appName("ETL_Mongo_Spark")
    .config("spark.mongodb.read.connection.uri", get_mongo_url(DB_SOURCE_MONGO))
    .config("spark.mongodb.write.connection.uri", get_mongo_url(DB_TARGET_MONGO))
    .config(
        "spark.jars.packages",
        "org.mongodb.spark:mongo-spark-connector_2.12:10.5.0,"
        "org.postgresql:postgresql:42.6.0"
    )
    .getOrCreate()
)


def read_table(spark_session, table_name: str):
    return (
        spark_session.read.format("jdbc")
        .option("url", _psql_url_music)
        .option("dbtable", table_name)
        .option("user", _creds_music["user"])
        .option("password", _creds_music["password"])
        .option("driver", driver)
        .load()
    )

def write_to_mongo(df, collection_name: str, mode: str = "overwrite"):
    df.write.format("mongodb") \
        .mode(mode) \
        .option("database", DB_TARGET_MONGO) \
        .option("collection", collection_name) \
        .save()

def get_top_n(df, partition_cols: list, order_col: str, n: int = 10):
    window_spec = Window.partitionBy(*partition_cols).orderBy(col(order_col).desc())
    return (
        df.withColumn("rank", row_number().over(window_spec))
          .filter(col("rank") <= n)
          .drop("rank")
    )

users_df = read_table(spark, "users")
tracks_df = read_table(spark, "tracks")
genres_df = read_table(spark, "genres")

activity_df = (
    spark.read.format("mongodb")
    .option("database", "db")
    .option("collection", COLLECTION_ACTIVITY)
    .load()
)

activity_users_df = activity_df.join(
    users_df, activity_df.user_id == users_df.id, how="left"
)

activity_tracks_users_df = activity_users_df.join(
    tracks_df, activity_users_df.track_id == tracks_df.id, how="left"
)

enriched_df = activity_tracks_users_df.join(
    genres_df, activity_tracks_users_df.genre_id == genres_df.id, how="left"
)

user_stats_df = (
    enriched_df.groupBy("user_id")
    .agg(
        count(when(col("event") == "play", True)).alias("tracks_listened"),
        count(when(col("event") == "skip", True)).alias("tracks_skipped")
    )
)


_to_write = [
    (activity_df,        "activities",           "overwrite"),
    (users_df,           "users",                "overwrite"),
    (tracks_df,          "tracks",               "overwrite"),
    (user_stats_df,      COLLECTION_RESULT,      "append")
]

for df_obj, coll_name, write_mode in _to_write:
    write_to_mongo(df_obj, coll_name, mode=write_mode)

logs_df = (
    enriched_df
    .withColumn("date",  to_date(col("time")))
    .withColumn("week",  weekofyear(col("time")))
    .withColumn("month", month(col("time")))
)

listened_df = logs_df.filter(col("event") == "play")

top_played = (
    activity_df.groupBy("track_id")
    .agg(count("*").alias("play_count"))
    .orderBy(col("play_count").desc())
)

top_skipped = (
    activity_df.filter(col("event") == "skip")
    .groupBy("track_id")
    .agg(count("*").alias("skip_count"))
    .orderBy(col("skip_count").desc())
)

top_genres_day   = listened_df.groupBy("date",  "genre_id").agg(count("*").alias("plays")).orderBy(desc("date"), desc("plays"))
top_genres_week  = listened_df.groupBy("week",  "genre_id").agg(count("*").alias("plays")).orderBy(desc("week"), desc("plays"))
top_genres_month = listened_df.groupBy("month", "genre_id").agg(count("*").alias("plays")).orderBy(desc("month"), desc("plays"))

top_tracks_day   = listened_df.groupBy("date",  "track_id").agg(count("*").alias("plays")).orderBy(desc("date"), desc("plays"))
top_tracks_week  = listened_df.groupBy("week",  "track_id").agg(count("*").alias("plays")).orderBy(desc("week"), desc("plays"))
top_tracks_month = listened_df.groupBy("month", "track_id").agg(count("*").alias("plays")).orderBy(desc("month"), desc("plays"))

top_genres_day_top10   = get_top_n(top_genres_day,   ["date"],  "plays", 10)
top_genres_week_top10  = get_top_n(top_genres_week,  ["week"],  "plays", 10)
top_genres_month_top10 = get_top_n(top_genres_month, ["month"], "plays", 10)

top_tracks_day_top10   = get_top_n(top_tracks_day,   ["date"],  "plays", 10)
top_tracks_week_top10  = get_top_n(top_tracks_week,  ["week"],  "plays", 10)
top_tracks_month_top10 = get_top_n(top_tracks_month, ["month"], "plays", 10)

_top_collections = [
    (top_played,               "top_played_tracks",    "append"),
    (top_skipped,              "top_skipped_tracks",   "append"),
    (top_genres_day_top10,     "top_genres_day",       "append"),
    (top_genres_week_top10,    "top_genres_week",      "append"),
    (top_genres_month_top10,   "top_genres_month",     "append"),
    (top_tracks_day_top10,     "top_tracks_day",       "append"),
    (top_tracks_week_top10,    "top_tracks_week",      "append"),
    (top_tracks_month_top10,   "top_tracks_month",     "append")
]

for df_obj, coll_name, write_mode in _top_collections:
    write_to_mongo(df_obj, coll_name, mode=write_mode)
