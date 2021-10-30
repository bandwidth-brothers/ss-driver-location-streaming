#!/bin/bash

aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 557623108041.dkr.ecr.us-west-2.amazonaws.com
docker build -t ss-spark-kinesis-streaming .
docker tag ss-spark-kinesis-streaming:latest 557623108041.dkr.ecr.us-west-2.amazonaws.com/ss-spark-kinesis-streaming:latest
docker push 557623108041.dkr.ecr.us-west-2.amazonaws.com/ss-spark-kinesis-streaming:latest
