# Lambda Logging Consumer

## Resources

* `aws_lambda_function.consumer_lambda` - the Lambda function
* `aws_lambda_event_source_mapping.lambda_kinesis_event_mapping` - Lambda/Kinesis event mapping
* `aws_cloudwatch_log_group.lambda_log_group` - log group for Lambda function
* `aws_iam_role.lambda_role` - IAM role for Lambda function
* `aws_iam_policy.lambda_logging_access` - policy for Lambda to talk to CloudWatch for logging
* `aws_iam_policy.lambda_kinesis_access` - policy for Lambda to talk to Kinesis
* `aws_iam_role_policy_attachment.lambda_logging_access_attach` - attach CloudWatch policy
* `aws_iam_role_policy_attachment.lambda_kineses_access_attach` - attach Kinesis policy

## Variables

* `lambda_function_name` - name of the Lambda function
* `kinesis_stream_arn` - arn of Kinesis stream
* `tags` - tags for the Lambda function
* `enabled` - whether the lambda should be created

## Outputs

* `lambda_function_name` - name of the lambda function
