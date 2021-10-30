import os
import sys
import json
import traceback

from datetime import datetime
from pyspark import SparkContext
from pyspark.sql import Row
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import to_date, col
from pyspark.streaming import StreamingContext
from pyspark.streaming.kinesis import KinesisUtils, InitialPositionInStream


def get_master():
    if len(sys.argv) == 2:
        return sys.argv[1]
    else:
        return "local[4]"


sc = SparkContext(get_master(), appName="DriverLocationApp")
ssc = StreamingContext(sc, 5)

kinesis = KinesisUtils.createStream(
    ssc,
    kinesisAppName="DriverLocationApp",
    streamName="DriverLocationStream",
    endpointUrl="https://kinesis.us-west-2.amazonaws.com",
    regionName="us-west-2",
    initialPositionInStream=InitialPositionInStream.LATEST,
    checkpointInterval=5,
    awsAccessKeyId=os.getenv('KINESIS_ACCESS_KEY_ID'),
    awsSecretKey=os.getenv('KINESIS_SECRET_KEY'))

schema = StructType([
    StructField("delivery_id", IntegerType()),
    StructField("driver_id", StringType()),
    StructField("lat", StringType()),
    StructField("lng", StringType()),
    StructField("timestamp", TimestampType())])

stsUserAccessKey = os.environ['STS_USER_ACCESS_KEY']
stsUserSecretKey = os.environ['STS_USER_SECRET_KEY']
ecsSparkRoleArn = os.environ['ECS_SPARK_ROLE_ARN']
s3BucketName = os.environ['S3_BUCKET_NAME']


def get_spark_session_instance(sparkConf):
    if "sparkSessionSingletonInstance" not in globals():
        globals()["sparkSessionSingletonInstance"] = SparkSession \
            .builder \
            .config(conf=sparkConf) \
            .getOrCreate()
    return globals()["sparkSessionSingletonInstance"]


def get_datetime(timestamp_str):
    return datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")


def dict_to_row(dct):
    return Row(delivery_id=dct['delivery_id'],
               driver_id=dct['driver_id'],
               lat=dct['lat'],
               lng=dct['lng'],
               timestamp=get_datetime(dct['timestamp']))


def write_to_s3(df, bucket_path, format='csv'):
    try:
        df \
            .coalesce(1) \
            .write.format(format) \
            .option('fs.s3a.access.key', stsUserAccessKey) \
            .option('fs.s3a.secret.key', stsUserSecretKey) \
            .option('header', True) \
            .save(f"s3a://{s3BucketName}/{bucket_path}", mode='overwrite')
        print("S3 file saved")
    except Exception as s3_ex:
        print("Could not save S3 file")
        print(traceback.format_exc())


def process(time, rdd):
    print(f"========== {time} ==========")
    try:
        if not rdd.isEmpty():
            spark = get_spark_session_instance(rdd.context.getConf())
            row_rdd = rdd.map(lambda data: json.loads(data)) \
                .map(dict_to_row)

            location_df = spark.createDataFrame(row_rdd, schema)
            location_df.show()

            # write original data
            write_to_s3(location_df, f"driver-location/{str(datetime.now()).replace(' ', '-')}-pings.parquet",
                        format='parquet')

            # transform data
            location_df = location_df \
                .withColumn('date', to_date(col('timestamp'), 'yyyy-MM-dd')) \
                .groupBy('driver_id', 'date') \
                .count() \
                .withColumnRenamed('count', 'total_pings')
            location_df.show()

            # write transformed data
            write_to_s3(location_df, f"driver-location-totals/{str(datetime.now()).replace(' ', '-')}-totals.csv",
                        format='csv')
        else:
            print("                RDD Empty                ")
    except Exception as ex:
        print(ex)
    print("=========================================")


kinesis.foreachRDD(process)

ssc.start()
ssc.awaitTermination()
