
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.59.0"
    }
  }

  required_version = ">= 1.0.0"
}

provider "aws" {
  region = var.aws_region
}

locals {
  tags = {
    Project = "ss-driver-location-streaming"
    Team    = "Data-Engineers"
    Env     = "CI/CD"
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.7.0"

  name                 = "jenkins-vpc"
  cidr                 = "10.0.0.0/16"
  azs                  = ["${var.aws_region}a"]
  public_subnets       = ["10.0.1.0/24"]
  private_subnets      = ["10.0.3.0/24"]
  enable_dns_hostnames = true
  enable_nat_gateway   = false

  vpc_tags = {
    Name = "jenkins-vpc"
  }
  tags = local.tags
}


data "aws_ami" "amz_linux_2" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-ebs"]
  }

  owners = ["amazon"]
}

resource "aws_instance" "jenkins" {
  ami                    = data.aws_ami.amz_linux_2.id
  user_data              = file("./userdata.sh")
  key_name               = var.key_name
  instance_type          = var.ec2_instance_type
  subnet_id              = module.vpc.public_subnets[0]
  vpc_security_group_ids = [aws_security_group.jenkins_sg.id]

  root_block_device {
    volume_size = 16
  }

  tags = {
    Name = "Scrumptious Jenkins"
  }
}

resource "aws_security_group" "jenkins_sg" {
  name        = "scrumptious_jenkins_sg"
  description = "Jenkins security group"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 22
    protocol    = "TCP"
    to_port     = 22
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    protocol    = "TCP"
    to_port     = 8080
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    protocol    = "-1"
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }
}
