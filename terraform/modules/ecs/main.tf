

terraform {
  required_providers {
    template = {
      source = "hashicorp/template"
    }
  }

  required_version = ">= 1.0.0"
}


locals {
  name               = "scrumptious-cluster"
  environment        = "dev"
  ec2_resources_name = "${local.name}-${local.environment}"

  tags = merge(var.tags, {
    Project     = "TestCluster"
    Environment = "Dev"
    Owner       = "PaulSamsotha"
  })
}

data "aws_availability_zones" "available" {
  state = "available"
}

# ECS Cluster
module "ecs" {
  source  = "terraform-aws-modules/ecs/aws"
  version = "3.4.0"

  name               = local.name
  container_insights = true

  capacity_providers = ["FARGATE", "FARGATE_SPOT", aws_ecs_capacity_provider.prov1.name]
  default_capacity_provider_strategy = [{
    capacity_provider = aws_ecs_capacity_provider.prov1.name # "FARGATE_SPOT"
    weight            = "1"
  }]

  tags = local.tags
}

module "ec2_profile" {
  source = "terraform-aws-modules/ecs/aws//modules/ecs-instance-profile"
  name   = local.name
  tags   = local.tags
}

resource "aws_ecs_capacity_provider" "prov1" {
  name = "prov1"

  auto_scaling_group_provider {
    auto_scaling_group_arn = module.asg.autoscaling_group_arn
  }
}

# Autoscaling Group
data "aws_ami" "amazon_linux_ecs" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn-ami-*-amazon-ecs-optimized"]
  }

  filter {
    name   = "owner-alias"
    values = ["amazon"]
  }
}

data "template_file" "user_data" {
  template = file("${path.module}/user_data.sh")

  vars = {
    cluster_name = local.name
  }
}

resource "aws_security_group" "spark_sg" {
  name        = "spark_ui_node_jupyter"
  description = "Allow access to spark and Jupyter"
  vpc_id      = var.vpc_id

  ingress {
    description = "Spark UI"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Spark Node port"
    from_port   = 7077
    to_port     = 7077
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Jupyter"
    from_port   = 8888
    to_port     = 8888
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "SSH to Instance"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

module "asg" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "~> 4.0"
  name    = local.ec2_resources_name

  # Launch configuration
  lc_name   = local.ec2_resources_name
  use_lc    = true
  create_lc = true

  image_id                  = data.aws_ami.amazon_linux_ecs.id
  instance_type             = var.ec2_instance_type
  key_name                  = var.key_name
  security_groups           = [aws_security_group.spark_sg.id, var.vpc_default_security_group_id]
  iam_instance_profile_name = module.ec2_profile.iam_instance_profile_id
  user_data                 = data.template_file.user_data.rendered

  # Auto scaling group
  vpc_zone_identifier         = var.vpc_zone_identifier
  health_check_type           = "EC2"
  min_size                    = 1
  max_size                    = 2
  desired_capacity            = 1 # we don't need them for the example
  wait_for_capacity_timeout   = 0
  associate_public_ip_address = true

  depends_on = [aws_security_group.spark_sg]

  tags = [local.tags]
}

