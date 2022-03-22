
resource "aws_s3_bucket" "data_lake" {
  bucket = var.bucket_name
  acl    = "private"

  lifecycle_rule {
    enabled = false

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 60
      storage_class = "GLACIER"
    }

    expiration {
      days = 180
    }
  }

  tags = var.tags
}

