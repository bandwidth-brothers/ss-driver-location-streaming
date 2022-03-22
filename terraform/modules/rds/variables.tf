
variable "enabled" {
  type        = bool
  default     = true
  description = "whether to create the database"
}

variable "db_name" {
  type        = string
  description = "name of the database"
}

variable "db_username" {
  type        = string
  description = "mysql database username"
}

variable "db_password" {
  type        = string
  description = "mysql database password"
}

variable "db_instance_class" {
  type        = string
  default     = "db.t3.micro"
  description = "instance class for rds instance"
}

variable "db_allocation_storage" {
  type        = number
  default     = 20
  description = "allocated storage for database (in gigabytes)"
}

variable "vpc_security_group_ids" {
  type        = list(string)
  default     = []
  description = "ids for security groups in vpc"
}

variable "db_subnet_ids" {
  type        = list(string)
  description = "list of subnet ids to put the database"
}

variable "db_publicly_accessible" {
  type        = bool
  default     = false
  description = "if the database is publicly accessible"
}

variable "vpc_id" {
  type        = string
  description = "vpc for database security group"
}

variable "tags" {
  type        = map(string)
  description = "tags for the rds instance"
}
