# ECS

## Modules

* [./spark_service](./spark_service/README.md)
* [terraform-aws-modules/ecs/aws](https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest)
* [terraform-aws-modules/ecs/aws//modules/ecs-instance-profile](https://registry.terraform.io/modules/terraform-aws-modules/ecs/aws/latest)
* [terraform-aws-modules/autoscaling/aws](https://registry.terraform.io/modules/HDE/autoscaling/aws/latest)

## Resources

* `aws_ecs_capacity_provider.prov1` - capacity provider for ECS cluster
* `aws_security_group.spark_sg` - security group for container instance

## Variables

* `key_name` - name of key pair for EC2 SSH access
* `ec2_instance_type` - type of EC2 container instance
* `vpc_id` - ID of the VPC
* `vpc_default_security_group_id` - ID of default security group
* `vpc_zone_identifier` - zone identifier for ASG (list of public/private subnet)
* `spark_docker_image` - fully qualified name of Spark Docker image
* `tags` - tags for ECS cluster resources
* `spark_container_env_vars` - environment variables for Spark Docker image (`list(map(string))`)
  
      [{name: "SOME_VAR", value: "some value"}]

## Outputs

* `spark_task_role_arn` - arn for the Spark ECS task