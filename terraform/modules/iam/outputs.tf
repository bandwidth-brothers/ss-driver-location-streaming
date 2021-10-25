
output "spark_sts_user_access_key" {
  value = aws_iam_access_key.spark_sts_user.id
}

output "spark_sts_user_secret_key" {
  value = aws_iam_access_key.spark_sts_user.secret
}
