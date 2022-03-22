# Jenkins Image/Container

* [Requirements to run Pipelines](#requirements-to-run-pipelines)
    * [Plugins](#plugins)
    * [Credentials](#credentials)
* [Run in Development](#run-in-development)
  
* [Pipelines](#pipelines)
    * [Driver Location Spark Pipeline](#driver-location-spark-pipeline)
    * [Driver Location Kinesis Retry Pipeline](#driver-location-kinesis-retry-pipeline)
    

## Requirements to run Pipelines

### Plugins

The following plugins need to be installed

* Docker Plugin
* Docker Pipeline Plugin
* Amazon ECR Plugin
* CloudBees AWS Credentials Plugin
* CloudBees Docker Build and Publish Plugin

### Credentials

The following credentials and API tokens needs to be created to run pipelines
and set up GitHub webhook

* `aws_creds` - create Jenkins global AWS credentials (used to push to ECR)
* `aws_user_pass` - create username/password credentials with access key as username and secret key as password (used to deploy stack)
* `GitHubWebhook` - go to user/Configure and add API token for webhook

## GitHub Webhook

1. Go to GitHub repository and click on project Settings
2. Click Webhooks in the left navigation
3. Click Add Webhook button and then login
4. For Payload URL put use `<Jenkin-Url>:port/github-webhook/`
5. For Secret use the `GitHubWebhook` token created in [Credentials](#credentials)
5. Click Add Webhook

The pipeline will need to have been run once before the Webhook will work.
Next push should trigger a build.

## Run in Development

There is a `docker-compose.yaml` file in this directory to run the Jenkins
container. A clean Jenkins will run. You will still need to manually install
all plugins and add the credentials listed above. To run the container, just
run `docker-compose up`.

## Pipelines

### Driver Location Spark Pipeline

#### Pipeline Parameters

* `STACK_NAME` - name of the CloudFormation stack used to deploy Spark
* `TEMPLATE_FILE` - CloudFormation template file used to deploy stack
* `PARAMETERS_FILE` - properties file used to override CloudFormation parameters
* `REGION` - AWS region where stack is deployed
* `GITHUB_ACCOUNT` - GitHub account of repository for this project (parameterized to use in development)
* `GIT_BRANCH` - Git branch of repository (parameterized for use in development)
* `DOCKER_IMAGE_NAME` - Docker image name to be pushed to ECR
* `AWS_ACCOUNT` - AWS account id (parameterized to push to different ECR repos)

### Driver Location Kinesis Retry Pipeline

#### Pipeline Parameters

* `STACK_NAME` - name of the CloudFormation stack used to deploy Spark
* `TEMPLATE_FILE` - CloudFormation template file used to deploy stack
* `PARAMETERS_FILE` - properties file used to override CloudFormation parameters
* `REGION` - AWS region where stack is deployed
* `GITHUB_ACCOUNT` - GitHub account of repository for this project (parameterized to use in development)
* `GIT_BRANCH` - Git branch of repository (parameterized for use in development)
* `DOCKER_IMAGE_NAME` - Docker image name to be pushed to ECR
* `AWS_ACCOUNT` - AWS account id (parameterized to push to different ECR repos)