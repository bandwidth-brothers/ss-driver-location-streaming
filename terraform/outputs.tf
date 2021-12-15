
output "s3_bucket_domain" {
  value = module.s3_bucket.s3_bucket_domain_name
}

output "s3_bucket_name" {
  value = module.s3_bucket.s3_bucket_name
}

output "rds_endpoint" {
  value = module.mysql_rds.db_endpoint
}

output "sqs_failover_queue_url" {
  value = module.sqs.failover_queue_url
}

output "dynamodb_failure_table_name" {
  value = module.dynamodb.table_name
}
