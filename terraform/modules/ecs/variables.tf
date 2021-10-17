

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "key_name" {
  type        = string
  description = "key pair name to SSH into instance"
}

variable "ec2_instance_type" {
  description = "type of ec2 instance"
}

variable "vpc_id" {}

variable "vpc_default_security_group_id" {}

variable "vpc_zone_identifier" {}

variable "spark_docker_image" {
  type = string
  description = "the spark docker image to run on ecs"
}

variable "tags" {
  default     = {}
  description = "tags for ecs cluster resources"
}
