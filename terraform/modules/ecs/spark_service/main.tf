
resource "aws_cloudwatch_log_group" "spark_log_group" {
  name              = "SparkLogGroup"
  retention_in_days = 1
}

resource "aws_ecs_service" "spark_service" {
  name            = "spark-ecs-service"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.spark_task.id

  desired_count = 1

  deployment_maximum_percent         = 100
  deployment_minimum_healthy_percent = 0
}

resource "aws_ecs_task_definition" "spark_task" {
  family             = "spark"
  cpu                = 512
  memory             = 2048
  execution_role_arn = aws_iam_role.task_execution_role.arn
  task_role_arn      = aws_iam_role.task_role.arn

  container_definitions = jsonencode([
    {
      name      = "spark-master"
      image     = var.spark_docker_image
      essential = true
      environment : concat(var.spark_container_env_vars,
        tolist([{ name : "ECS_SPARK_ROLE_ARN", value : aws_iam_role.task_role.arn }])
      )
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        },
        {
          containerPort = 7077
          hostPort      = 7077
        },
        {
          containerPort = 8888
          hostPort      = 8888
        }
      ],
      logConfiguration : {
        logDriver : "awslogs",
        options : {
          "awslogs-region" : "${var.aws_region}",
          "awslogs-group" : "${aws_cloudwatch_log_group.spark_log_group.name}",
          "awslogs-stream-prefix" : "spark-ecs"
        }
      }
    }
  ])
  tags = var.tags
}

resource "aws_iam_role" "task_execution_role" {
  name = "ECSTaskExecutionRole"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role" "task_role" {
  name = "ECSSparkTaskRole"

  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "",
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "ecs-tasks.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "spark_kinesis_access_policy" {
  name        = "SparkKinesisAccess"
  path        = "/policy/kinesis/"
  description = "IAM policy for Spark to access Kinesis streams"

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
          "kinesis:SubscribeToShard",
          "dynamodb:DescribeTable",
          "dynamodb:CreateTable",
          "dynamodb:Scan",
          "dynamodb:GetItem",
          "dynamodb:BatchGetItem",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:BatchWriteItem",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "cloudwatch:GetMetricData",
          "cloudwatch:PutMetricData",
          "cloudwatch:CreateLogStream",
          "sts:*"
        ]
        "Resource" : "*"
      }
    ]
  })
}

# Policy for ECS Agent to talk to ECS
resource "aws_iam_role_policy_attachment" "execution_policy_attach" {
  role       = aws_iam_role.task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Policy for Spark container to talk to Kinesis
resource "aws_iam_role_policy_attachment" "spark_kinesis_access_policy_attach" {
  role       = aws_iam_role.task_role.name
  policy_arn = aws_iam_policy.spark_kinesis_access_policy.arn
}

# Policy Spark to talk to S3
# TODO: create stricter policy
resource "aws_iam_role_policy_attachment" "s3_policy_attach" {
  role       = aws_iam_role.task_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}
