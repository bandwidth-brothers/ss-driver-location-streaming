
variable "lambda_function_name" {
  type        = string
  description = "name of the Lambda function"
}

variable "tags" {
  type        = map(string)
  description = "tags for the Lambda function"
}

variable "kinesis_stream_arn" {
  type        = string
  description = "arn of Kinesis stream"
}

variable "enabled" {
  type        = bool
  default     = true
  description = "whether the lambda should be created"
}
