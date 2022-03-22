# Spark Cluster

## CloudFormation

The Spark cluster is run as an ECS task/service.

### Resources

`DriverLocationProducerTask` - ECS task to run the Spark Docker container
`DriverLocationProducerService` - ECS service to manage the task
`TaskExecutionRole` - ECS execution role for the task to talk to the ECS agent
`TaskRole` - task role with any permissions required for the Spark container
`CloudWatchLogGroup` - log group for spark container logging
`SparkAwsUser` - user for spark to talk to S3

## Docker Image

### Files copied to image

* `kinesis_stream.py` - Spark Streaming application
* `jupup.sh` - script to run Jupyter Lab
* `runstream.sh` - script to start Spark Streaming application
* `transform_demo.ipynb` - Jupyter Notebook with demo transformation
