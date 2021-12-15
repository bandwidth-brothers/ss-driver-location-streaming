# DynamoDb Table for Failover

This DynamoDB table is used for failover. When the driver locations cannot
be streamed to Kinesis, they will be stored in this table for later retrieval.

## Resources

`aws_dynamodb_table.failover_table` - dynamodb table for failover

## Variables

* `table_name` - name of dynamodb table
* `read_capacity` - read capacity units for table (default 5)
* `write_capacity` - write capacity units for table (default 5)

## Outputs

* `table_name` - the name of the dynamodb table
