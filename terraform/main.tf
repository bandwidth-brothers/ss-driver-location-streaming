
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
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "3.7.0"

  name                 = "ecs-cluster-vpc"
  cidr                 = "10.0.0.0/16"
  azs                  = ["${var.aws_region}a", "${var.aws_region}b"]
  public_subnets       = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets      = ["10.0.3.0/24", "10.0.4.0/24"]
  enable_dns_hostnames = true
  enable_nat_gateway   = false

  vpc_tags = {
    Name = "ecs-cluster-vpc"
  }
  tags = local.tags
}

module "kinesis" {
  source      = "./modules/kinesis"
  stream_name = "DriverLocationStream"
  aws_region  = var.aws_region
  shard_count = var.kinesis_shard_count
  tags        = local.tags
}

module "spark_ecs" {
  source                        = "./modules/ecs"
  aws_region                    = var.aws_region
  ec2_instance_type             = var.ec2_type
  key_name                      = var.key_name
  spark_docker_image            = var.spark_docker_image
  vpc_id                        = module.vpc.vpc_id
  vpc_zone_identifier           = module.vpc.public_subnets
  vpc_default_security_group_id = module.vpc.default_security_group_id
}

module "lambda" {
  source               = "./modules/lambda"
  count                = var.with_lambda_consumer ? 1 : 0
  aws_region           = var.aws_region
  lambda_function_name = "DriverLocationConsumerFunction"
  kinesis_stream_arn   = module.kinesis.stream_arn
  tags                 = local.tags
}
