
variable "aws_region" {
  type        = string
  description = "AWS region for the Kinesis stream and Lambda"
}

variable "kinesis_shard_count" {
  type        = number
  default     = 3
  description = "number of shards for Kinesis"
}

variable "key_name" {
  type        = string
  description = "name of the keypair for ec2 ssh access"
}

variable "ec2_instance_type" {
  type        = string
  default     = "t3.medium"
  description = "the ec2 type for the container instance"
}

variable "s3_bucket_name" {
  type        = string
  description = "name of the s3 bucket to load location data"
}

variable "lambda_enabled" {
  type        = bool
  default     = true
  description = "whether to include lambda consumer"
}

variable "rds_username" {
  type        = string
  description = "username for the rds instance"
}

variable "rds_password" {
  type        = string
  description = "password for the rds instance"
}

variable "rds_publicly_accessible" {
  type        = bool
  description = "whether the rds instance is publicly available"
}

variable "rds_db_name" {
  type        = string
  description = "name of the database in the rds instance"
}

variable "rds_enabled" {
  type = bool
  description = "whether to create the rds instance"
}

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

variable "spark_ecs_cluster_name" {
  type = string
  description = "ECS cluster to put Spark"
}