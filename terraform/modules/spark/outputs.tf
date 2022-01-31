
output "og_pings_failover_queue_url" {
  value = var.enabled ? aws_sqs_queue.og_pings_failure_queue[0].url : "og pings failover queue disabled"
}

output "transformed_pings_failover_queue_url" {
  value = var.enabled ? aws_sqs_queue.transformed_pings_failure_queue[0].url : "transformed pings failover queue disabled"
}

