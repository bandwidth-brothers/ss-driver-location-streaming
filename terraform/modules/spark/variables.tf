
variable "enabled" {
  type        = bool
  default     = true
  description = "whether spark is enabled"
}

variable "spark_cfn_stack_name" {
  type    = string
  default = "DriverLocationSpark"
}

variable "spark_cfn_docker_image" {
  type = string
}

variable "spark_cfn_s3_bucket_name" {
  type        = string
  description = "S3 bucket for Spark to load data"
}

variable "ecs_cluster_name" {
  type        = string
  description = "ECS cluster to put Spark"
}

variable "awslogs_region" {
  type        = string
  description = "AWS region for awslogs"
}

variable "sqs_og_pings_queue_name" {
  type        = string
  default     = "SparkDriverLocationOgPingsFailure"
  description = "name of the SQS queue used for Spark original pings failure"
}

variable "sqs_transformed_pings_queue_name" {
  type        = string
  default     = "SparkDriverLocationTransformedPingsFailure"
  description = "name of the SQS queue used for Spark transformed pings failure"
}

