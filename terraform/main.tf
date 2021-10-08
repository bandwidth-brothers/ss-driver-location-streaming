
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

module "kinesis" {
  source      = "./modules/kinesis"
  aws_region  = var.aws_region
  stream_name = "DriverLocationStream"
  tags        = local.tags
}

module "lambda" {
  source               = "./modules/lambda"
  aws_region           = var.aws_region
  lambda_function_name = "DriverLocationConsumerFunction"
  kinesis_stream_arn   = module.kinesis.stream_arn
  tags                 = local.tags
}
