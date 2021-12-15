
resource "aws_dynamodb_table" "failover_table" {
  count          = var.enabled ? 1 : 0
  hash_key       = "Timestamp"
  name           = var.table_name
  billing_mode   = "PROVISIONED"
  write_capacity = var.read_capacity
  read_capacity  = var.write_capacity

  attribute {
    name = "Timestamp"
    type = "S"
  }
}
