# Jenkins Image/Container

## Plugins

The following plugins need to be installed

* Docker Plugin
* Docker Pipeline Plugin
* Amazon ECR Plugin
* CloudBees AWS Credentials Plugin
* CloudBees Docker Build and Publish Plugin

## Credentials

* `aws_cred` - create Jenkins global AWS credentials
* `GitHubWebhook` - go to user/Configure and add API token for webhook
* `IAM Role` - create an IAM role for CloudFormation to create resources.
