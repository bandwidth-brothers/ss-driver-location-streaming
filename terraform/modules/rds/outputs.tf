
output "db_endpoint" {
  value = var.enabled ? aws_db_instance.mysql[0].endpoint : "rds not enabled"
}

