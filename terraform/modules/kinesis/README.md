# Kinesis Data Stream

## Resources

* `aws_kinesis_stream.driver_location_stream` - Kinesis data stream

## Variables

* `aws_region` - AWS region for the Kinesis stream
* `stream_name` - name of the Kinesis stream
* `shard_count` - number of shared for the Kinesis stream
* `retention_period` - how long data should be accessible (in hours gt 24)
* `tags` - tags for the Kinesis stream

## Outputs

* `stream_name` - name of the Kinesis stream
* `stream_arn` - arn of the Kinesis stream
