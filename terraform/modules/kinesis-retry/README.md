# Cloudformation Stack for Driver Location Kinesis Retry Handling

## Resources

* `aws_cloudformation_stack.kinesis_retry_stack` - CloudFormation stack

## Variables

* `kinesis_retry_cfn_stack_name` - name of the Cloudformation stack
* `kinesis_retry_cfn_docker_image` - Docker image to use for ECS task
* `ecs_cluster_name` - name of the ECS cluster
* `awslogs_region` - AWS region for awslogs