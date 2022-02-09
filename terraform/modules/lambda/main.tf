
locals {
  jar_file    = "${path.module}/data-location-lambda-consumer.jar"
  policy_path = "/policy/lambda/"
}

resource "aws_lambda_function" "consumer_lambda" {
  count            = var.enabled ? 1 : 0
  function_name    = var.lambda_function_name
  filename         = local.jar_file
  handler          = "com.ss.scrumptious.consumer.DriverLocationConsumer::handleRequest"
  runtime          = "java11"
  role             = aws_iam_role.lambda_role.arn
  source_code_hash = filebase64sha256(local.jar_file)

  depends_on = [
    aws_iam_role_policy_attachment.lambda_logging_access_attach,
    aws_iam_role_policy_attachment.lambda_kineses_access_attach,
    aws_cloudwatch_log_group.lambda_log_group
  ]

  tags = {
    Project = "ss-driver-location-streaming"
    Team    = "Data-Engineers"
  }
}

resource "aws_lambda_event_source_mapping" "lambda_kinesis_event_mapping" {
  count             = var.enabled ? 1 : 0
  event_source_arn  = var.kinesis_stream_arn
  function_name     = aws_lambda_function.consumer_lambda[0].arn
  starting_position = "LATEST"
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  count             = var.enabled ? 1 : 0
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = 14
}

resource "aws_iam_role" "lambda_role" {
  name = "LambdaKinesisRole"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : "sts:AssumeRole",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Effect" : "Allow",
        "Sid" : ""
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_logging_access" {
  name        = "LambdaCloudWatchLogging"
  path        = local.policy_path
  description = "IAM policy for logging from a lambda"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Action" : [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "arn:aws:logs:*:*:*",
        "Effect" : "Allow"
      }
    ]
  })
}

resource "aws_iam_policy" "lambda_kinesis_access" {
  name        = "LambdaKinesisAccess"
  path        = local.policy_path
  description = "IAM policy for Lambda to access Kinesis streams"

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "kinesis:DescribeStream",
          "kinesis:DescribeStreamSummary",
          "kinesis:GetRecords",
          "kinesis:GetShardIterator",
          "kinesis:ListShards",
          "kinesis:ListStreams",
          "kinesis:SubscribeToShard"
        ]
        "Resource" : "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logging_access_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_logging_access.arn
}

resource "aws_iam_role_policy_attachment" "lambda_kineses_access_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_kinesis_access.arn
}
