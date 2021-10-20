
output "s3_bucket_domain_name" {
  value = aws_s3_bucket.data_lake.bucket_domain_name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.data_lake.bucket
}
