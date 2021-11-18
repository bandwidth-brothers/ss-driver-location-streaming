
variable "spark_cfn_stack_name" {
  type = string
  default = "DriverLocationSpark"
}

variable "spark_cfn_docker_image" {
  type = string
}

variable "spark_cfn_s3_bucket_name" {
  type = string
  description = "S3 bucket for Spark to load data"
}

variable "ecs_cluster_name" {
  type = string
  description = "ECS cluster to put Spark"
}

variable "awslogs_region" {
  type = string
  description = "AWS region for awslogs"
}

