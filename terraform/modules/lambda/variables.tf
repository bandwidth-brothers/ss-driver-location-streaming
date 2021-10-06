
variable "aws_region" {
  type        = string
  description = "AWS region for the Lambda function"
}

variable "lambda_function_name" {
  type        = string
  description = "Name of the Lambda function"
}

variable "tags" {
  type        = map(string)
  description = "Tags for the Lambda function"
}

variable "kinesis_stream_arn" {
  type        = string
  description = "ARN of Kinesis stream"
}

