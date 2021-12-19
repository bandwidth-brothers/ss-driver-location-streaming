
resource "aws_sqs_queue" "failover_queue" {
  name = var.queue_name
}
