
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.59.0"
    }
  }

  required_version = ">= 1.0.0"
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
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
  enabled     = var.kinesis_enabled
  shard_count = var.kinesis_shard_count
  tags        = local.tags
}

module "ecs_cluster" {
  source                        = "./modules/ecs"
  ec2_instance_type             = var.ec2_instance_type
  key_name                      = var.key_name
  vpc_id                        = module.vpc.vpc_id
  vpc_zone_identifier           = module.vpc.public_subnets
  vpc_default_security_group_id = module.vpc.default_security_group_id

  tags = local.tags
}

module "spark_cfn_stack" {
  source                   = "./modules/spark"
  enabled                  = var.spark_enabled
  awslogs_region           = var.aws_region
  ecs_cluster_name         = module.ecs_cluster.cluster_name
  spark_cfn_docker_image   = var.spark_cfn_docker_image
  spark_cfn_s3_bucket_name = var.spark_cfn_s3_bucket_name

  depends_on = [module.ecs_cluster, module.s3_bucket]
}

module "kinesis_retry" {
  source                         = "./modules/kinesis-retry"
  awslogs_region                 = var.aws_region
  ecs_cluster_name               = module.ecs_cluster.cluster_name
  kinesis_retry_cfn_docker_image = var.kinesis_retry_cfn_docker_image
  failover_queue_url             = module.sqs.failover_queue_url

  depends_on = [module.kinesis, module.ecs_cluster]
}

module "s3_bucket" {
  source      = "./modules/s3"
  bucket_name = var.s3_bucket_name
  tags        = local.tags
}

module "mysql_rds" {
  source                 = "./modules/rds"
  enabled                = var.rds_enabled
  db_name                = var.rds_db_name
  db_username            = var.rds_username
  db_password            = var.rds_password
  db_publicly_accessible = var.rds_publicly_accessible
  vpc_id                 = module.vpc.vpc_id
  db_subnet_ids          = var.rds_publicly_accessible ? module.vpc.public_subnets : module.vpc.private_subnets
  tags                   = local.tags
}

module "sqs" {
  source = "./modules/sqs"
}

module "dynamodb" {
  source  = "./modules/dynamodb"
  enabled = var.dynamodb_enabled
}

module "lambda" {
  source               = "./modules/lambda"
  lambda_function_name = "DriverLocationConsumerFunction"
  enabled              = var.lambda_enabled
  kinesis_stream_arn   = module.kinesis.stream_arn
  tags                 = local.tags
}
