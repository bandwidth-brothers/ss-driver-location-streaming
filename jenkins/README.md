# Jenkins Image/Container

## Requirements to run Pipelines

### Plugins

The following plugins need to be installed

* Docker Plugin
* Docker Pipeline Plugin
* Amazon ECR Plugin
* CloudBees AWS Credentials Plugin
* CloudBees Docker Build and Publish Plugin

### Credentials

* `aws_creds` - create Jenkins global AWS credentials
* `GitHubWebhook` - go to user/Configure and add API token for webhook
* `IAM Role` - create an IAM role for CloudFormation to create resources.


## Run in Development

There is a `docker-compose.yaml` file in this directory to run the Jenkins
container. A clean Jenkins will run. You will still need to manually install
all plugins and add the credentials listed above. To run the container, just
run `docker-compose up`.