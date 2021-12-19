
resource "aws_cloudformation_stack" "spark_stack" {
  count = var.enabled ? 1 : 0
  name  = var.spark_cfn_stack_name
  parameters = {
    DockerImage      = var.spark_cfn_docker_image
    S3BucketName     = var.spark_cfn_s3_bucket_name
    AwsDefaultRegion = var.awslogs_region
    EcsClusterName   = var.ecs_cluster_name
  }

  template_body = file("../spark/cloudformation/ecs-spark-task-template.yaml")
  capabilities  = ["CAPABILITY_NAMED_IAM"]
  on_failure    = "DELETE"
}
