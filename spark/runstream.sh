#!/bin/bash

if [ -z "$KINESIS_ACCESS_KEY_ID" ]; then
  echo "KINESIS_ACCESS_KEY_ID not set. AWS service role should be active"
fi
if [ -z "$KINESIS_SECRET_KEY" ]; then
  echo "KINESIS_SECRET_KEY not set. AWS service role should be active"
fi

if [ "$1" == "--master" ]; then
  MASTER_ARG="--master $2"
else
  MASTER_ARG=""
fi

"${SPARK_HOME}/bin/spark-submit" \
  --packages "org.apache.spark:spark-streaming-kinesis-asl_2.12:3.1.2" $MASTER_ARG \
  "${SPARK_HOME}/work/app/kinesis_stream.py" $2
