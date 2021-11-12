
output "s3_bucket_domain" {
  value = module.s3_bucket.s3_bucket_domain_name
}

output "s3_bucket_name" {
  value = module.s3_bucket.s3_bucket_name
}

#output "spark_sts_user_access_key" {
#  value = module.spark_sts_user.spark_sts_user_access_key
#}

#output "spark_sts_user_secret_key" {
#  value     = module.spark_sts_user.spark_sts_user_secret_key
#  sensitive = true
#}

#output "ecs_spark_role_arn" {
#  value = module.spark_ecs.spark_task_role_arn
#}

output "rds_endpoint" {
  value = module.mysql_rds.db_endpoint
}
