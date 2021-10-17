
variable "aws_region" {
  type        = string
  description = "AWS region for the Kinesis stream and Lambda"
}

variable "kinesis_shard_count" {
  type        = number
  default     = 3
  description = "Number of shards for Kinesis"
}

variable "spark_docker_image" {
  type = string
  description = "the spark docker image to run on ecs"
}

variable "key_name" {
  type = string
  description = "name of the keypair for ec2 ssh access"
}

variable "ec2_type" {
  type = string
  default = "t3.medium"
  description = "the ec2 type for the container instance"
}

variable "with_lambda_consumer" {
  type = bool
  default = true
  description = "whether to include lambda consumer"
}
