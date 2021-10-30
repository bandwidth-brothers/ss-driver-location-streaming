

data "aws_iam_group" "admin_group" {
  group_name = "Administrators"
}

resource "aws_iam_user" "spark_sts_credentials_user" {
  name = "spark_sts_credentials_user"
  path = "/spark/"
  tags = var.tags
}

resource "aws_iam_user_group_membership" "admin_group_membership" {
  user   = aws_iam_user.spark_sts_credentials_user.name
  groups = [data.aws_iam_group.admin_group.group_name]
}

resource "aws_iam_access_key" "spark_sts_user" {
  user = aws_iam_user.spark_sts_credentials_user.name
}

resource "aws_iam_user_policy" "spark_sts_policy" {
  user = aws_iam_user.spark_sts_credentials_user.name
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : [
          "sts:*"
        ],
        "Effect" : "Allow",
        "Resource" : "*"
      }
    ]
  })
}
