
# Spark CloudFormation Stack

## Resources

* `aws_cloudformation_stack.spark_stack` - CloudFormation stack

## Variables

* `enabled` - whether Spark is enabled
* `spark_cfn_stack_name` - name of the CloudFormation stack
* `spark_cfn_docker_image` - Docker image to be used for task
* `spark_cfn_s3_bucket_name` - S3 bucket for Spark to load data
* `awslogs_region` - AWS region for awslogs
* `ecs_cluster_name` - ECS cluster to put Spark
