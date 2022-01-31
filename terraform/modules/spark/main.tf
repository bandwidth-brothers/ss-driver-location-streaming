
resource "aws_cloudformation_stack" "spark_stack" {
  count = var.enabled ? 1 : 0
  name  = var.spark_cfn_stack_name
  parameters = {
    DockerImage                      = var.spark_cfn_docker_image
    S3BucketName                     = var.spark_cfn_s3_bucket_name
    AwsDefaultRegion                 = var.awslogs_region
    EcsClusterName                   = var.ecs_cluster_name
    OgPingsFailoverQueueUrl          = aws_sqs_queue.og_pings_failure_queue[0].url
    TransformedPingsFailoverQueueUrl = aws_sqs_queue.transformed_pings_failure_queue[0].url
  }

  template_body = file("../spark/cloudformation/ecs-spark-task-template.yaml")
  capabilities  = ["CAPABILITY_NAMED_IAM"]
  on_failure    = "DELETE"

  depends_on = [
    aws_sqs_queue.og_pings_failure_queue,
    aws_sqs_queue.transformed_pings_failure_queue
  ]
}

resource "aws_sqs_queue" "og_pings_failure_queue" {
  count = var.enabled ? 1 : 0
  name  = var.sqs_og_pings_queue_name
}

resource "aws_sqs_queue" "transformed_pings_failure_queue" {
  count = var.enabled ? 1 : 0
  name  = var.sqs_transformed_pings_queue_name
}
