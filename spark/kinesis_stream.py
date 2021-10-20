import os
import sys
import json
import traceback

from datetime import datetime
from pyspark import SparkContext
from pyspark.sql import Row
from pyspark.sql import SparkSession
from pyspark.sql.types import *
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
    StructField("lng", StringType())])

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


def dict_to_row(dct):
    return Row(delivery_id=dct['delivery_id'],
               driver_id=dct['driver_id'],
               lat=dct['lat'],
               lng=dct['lng'])


def process(time, rdd):
    print(f"========== {time} ==========")
    try:
        if not rdd.isEmpty():
            spark = get_spark_session_instance(rdd.context.getConf())
            row_rdd = rdd.map(lambda data: json.loads(data)) \
                .map(dict_to_row)

            location_df = spark.createDataFrame(row_rdd, schema)
            location_df.show()
            try:
                location_df \
                    .coalesce(1) \
                    .write.format('csv') \
                    .option('fs.s3a.access.key', stsUserAccessKey) \
                    .option('fs.s3a.secret.key', stsUserSecretKey) \
                    .option('header', True) \
                    .save(f"s3a://{s3BucketName}/geolocation/{str(datetime.now()).replace(' ', '-')}-locations.csv", mode='overwrite')
                print("S3 file saved")
            except Exception as s3_ex:
                print("Could not save S3 file")
                print(traceback.format_exc())
        else:
            print("                RDD Empty                ")
    except Exception as ex:
        print(ex)
    print("=========================================")


kinesis.foreachRDD(process)

ssc.start()
ssc.awaitTermination()
