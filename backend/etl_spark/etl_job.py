from configs.database import get_mongo_url, get_psql_url
from pyspark.sql SparkSession


spark = SparkSession.builder \
        .appName("ETL_Mongo_Spark") \
        .config("spark.mongodb.read.connection.uri", get_mongo_url("user_activity")) \
        .config("spark.mongodb.write.connection.uri", get_mongo_url("daily-user_activity")) \
        .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:10.1.1") \
        .getOrCreate()

activity_df = spark.read.format("mongodb") \
        .option("database", "user_activity") \
        .option("collection", "user-activity") \
        .load()
