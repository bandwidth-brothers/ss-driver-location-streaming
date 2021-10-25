
variable "aws_region" {
  type        = string
  description = "AWS region for the Kinesis stream"
}

variable "stream_name" {
  type        = string
  description = "name of the Kinesis stream"
}

variable "shard_count" {
  type        = number
  default     = 1
  description = "number of shared for the Kinesis stream"
}

variable "retention_period" {
  type        = number
  default     = 24
  description = "how long data should be accessible (in hours gt 24)"
}

variable "tags" {
  type        = map(string)
  description = "tags for the Kinesis stream"
}
