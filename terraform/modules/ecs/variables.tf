
variable "key_name" {
  type        = string
  description = "key pair name to SSH into instance"
}

variable "ec2_instance_type" {
  description = "type of ec2 instance"
}

variable "vpc_id" {
  type        = string
  description = "id of the VPC"
}

variable "vpc_default_security_group_id" {
  type        = string
  description = "id of the default security group"
}

variable "vpc_zone_identifier" {
  type        = list(string)
  description = "zone identifier for ASG (list of public/private subnet)"
}

#variable "spark_docker_image" {
#  type        = string
#  description = "the spark docker image to run on ecs"
#}

variable "spark_container_env_vars" {
  type        = list(map(string))
  default     = []
  description = "environment variables for the spark container"
}

variable "tags" {
  default     = {}
  description = "tags for ecs cluster resources"
}
