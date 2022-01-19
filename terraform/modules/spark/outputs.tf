
output "failover_queue_url" {
  value = var.enabled ? aws_sqs_queue.spark_failure_queue[0].url : "failover queue disabled"
}
