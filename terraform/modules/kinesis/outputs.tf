
output "stream_name" {
  value = var.enabled ? aws_kinesis_stream.driver_location_stream[0].name : "Kinesis disabled"
}

output "stream_arn" {
  value = var.enabled ? aws_kinesis_stream.driver_location_stream[0].arn : "Kinesis disabled"
}
