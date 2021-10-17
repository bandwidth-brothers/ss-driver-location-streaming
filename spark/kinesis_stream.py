import os
import sys
import json

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
        return "local[2]"


sc = SparkContext(get_master(), appName="DriverLocationApp")
ssc = StreamingContext(sc, 3)

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
        spark = get_spark_session_instance(rdd.context.getConf())
        row_rdd = rdd.map(lambda data: json.loads(data)) \
            .map(dict_to_row)

        location_df = spark.createDataFrame(row_rdd, schema)
        location_df.show()
    except Exception as ex:
        print(ex)


kinesis.foreachRDD(process)

ssc.start()
ssc.awaitTermination()
