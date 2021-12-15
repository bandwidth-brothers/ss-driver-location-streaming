
variable "enabled" {
  type        = bool
  default     = true
  description = "whether dynamodb failure table is enabled"
}

variable "table_name" {
  type        = string
  default     = "DriverLocationKinesisFailure"
  description = "name of dynamodb table"
}

variable "read_capacity" {
  type        = number
  default     = 5
  description = "read capacity units for table"
}

variable "write_capacity" {
  type        = number
  default     = 5
  description = "write capacity units for table"
}
