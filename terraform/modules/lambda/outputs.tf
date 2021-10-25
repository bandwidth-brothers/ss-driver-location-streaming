
output "lambda_function_name" {
  value = var.enabled ? aws_lambda_function.consumer_lambda[0].function_name : "Lambda not enabled"
}
