
output "failover_queue_url" {
  value = aws_sqs_queue.failover_queue.url
}
