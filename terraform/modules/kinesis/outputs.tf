
output "stream_name" {
  value = aws_kinesis_stream.driver_location_stream.name
}

output "stream_arn" {
  value = aws_kinesis_stream.driver_location_stream.arn
}
