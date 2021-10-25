# Spark ECS Service

## Resources

* `aws_cloudwatch_log_group.spark_log_group` - log group for Spark logging
* `aws_ecs_service.spark_service` - Spark ECS service
* `aws_ecs_task_definition.spark_task` - Spark ECS task definition
* `aws_iam_role.task_execution_role` - Container instance task execution role
* `aws_iam_role.task_role` - service role for Spark task
* `aws_iam_policy.spark_kinesis_access_policy` - policy for Spark to talk to Kinesis
* `aws_iam_role_policy_attachment.execution_policy_attach` - policy attachment for execution role
* `aws_iam_role_policy_attachment.spark_kinesis_access_policy_attach` - policy attachment for Kinesis policy
* `aws_iam_role_policy_attachment.s3_policy_attach` - policy attachment for S3 access policy

## Variables

* `cluster_id` - id of the ECS cluster
* `spark_docker_image` - fully qualified name of Spark Docker image
* `aws_region` - AWS region for the service
* `tags` - tags for the service
* `spark_container_env_vars` - environment variables for Spark Docker image (`list(map(string))`)
  
      [{name: "SOME_VAR", value: "some value"}]

## Outputs

* `spark_task_role_arn` - arn for the Spark ECS task