
variable "cluster_id" {
  description = "id of the ECS cluster"
}

variable "tags" {
  default     = {}
  description = "tags for the task definition"
}

variable "aws_region" {
  description = "aws region"
}

variable "spark_docker_image" {
  type        = string
  description = "the spark docker image to run on ecs"
}

variable "spark_container_env_vars" {
  type        = list(map(string))
  default     = []
  description = "environment variables for the spark container"
}
