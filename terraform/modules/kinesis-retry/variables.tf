
variable "kinesis_retry_cfn_stack_name" {
  type        = string
  default     = "DriverLocationKinesisRetry"
  description = "name of the Cloudformation stack"
}

variable "kinesis_retry_cfn_docker_image" {
  type        = string
  description = "Docker image to use for ECS task"
}

variable "failover_queue_url" {
  type        = string
  description = "failover SQS queue url"
}

variable "ecs_cluster_name" {
  type        = string
  description = "name of the ECS cluster"
}

variable "awslogs_region" {
  type        = string
  description = "AWS region for awslogs"
}

