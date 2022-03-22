#!/bin/bash

echo 'scripts/ecr.sh has replaced this script.' && exit 0

cd spark 2>/dev/null || (echo 'No spark dir' && exit 1)
read -rp 'Enter AWS account ID: ' ACCOUNT

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin "${ACCOUNT}".dkr.ecr.us-west-2.amazonaws.com
docker build -t ss-spark-kinesis-streaming .
docker tag ss-spark-kinesis-streaming:latest "${ACCOUNT}".dkr.ecr.us-west-2.amazonaws.com/ss-spark-kinesis-streaming:latest
docker push "${ACCOUNT}".dkr.ecr.us-west-2.amazonaws.com/ss-spark-kinesis-streaming:latest
