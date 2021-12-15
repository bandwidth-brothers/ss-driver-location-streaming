
variable "aws_region" {
  type        = string
  description = "aws region for ec2"
}

variable "key_name" {
  type        = string
  description = "name of keypair for ssh access to ec2"
}

variable "ec2_instance_type" {
  type        = string
  default     = "t3.medium"
  description = "ec2 instance type"
}

variable "ebs_volume_name" {
  type = string
  default = "/dev/sdh"
  description = "name for the ebs volume for jenkins instance"
}
