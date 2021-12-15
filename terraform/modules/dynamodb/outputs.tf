
output "table_name" {
  value = var.enabled ? aws_dynamodb_table.failover_table[0].name : "table not enabled"
}
