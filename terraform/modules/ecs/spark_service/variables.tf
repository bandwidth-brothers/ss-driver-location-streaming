
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

variable "ec2_instance_type" {
  type        = string
  description = "type of ec2 instance"
}

variable "spark_docker_image" {
  type = string
  description = "the spark docker image to run on ecs"
}
