# IAM

## Resources

* `aws_iam_user.spark_sts_credentials_user` - user for Spark access to AWS resources
* `aws_iam_user_group_membership.admin_group_membership` - group membership for Spark user
* `aws_iam_access_key.spark_sts_user` - access key for Spark user
* `aws_iam_user_policy.spark_sts_policy` - policy for Spark user

## Variables

* `tags` - tags for spark iam user

## Outputs

* `spark_sts_user_access_key` - access key for Spark IAM user
* `spark_sts_user_secret_key` - key for Spark IAM user