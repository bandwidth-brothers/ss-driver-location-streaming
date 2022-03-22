# Scripts

## `ecr.sh`

* `scripts/ecr.sh` - Builds Docker image and pushes it to ECR. This script can be used with different accounts and images. Just answer the prompts. The ECR repository should already be present in the AWS account.
    * **Example prompt:**
      ```
      Enter AWS account ID: 419106922284
      Enter AWS profile: ss
      Enter AWS region: us-west-2
      Enter Docker context: spark
      Enter Dockerfile: spark/Dockerfile
      Enter image name: ss-spark-kinesis-streaming
      ```

## `jenkins.sh`

### Jenkins Docker Image

* `scripts/jenkins.sh docker build` - build the docker image
    * `--name` - name of the Docker image
* `scripts/jenkins.sh docker push` - pushes the image to DockerHub

### Jenkins Terraform Infrastructure

* `scripts/jenkins.sh tf up -var-file='dev.tfvars'` - deploys the infrastructure
* `scripts/jenkins.sh tf down -var-file='dev.tfvars'` - tears down the infrastructure

All Terraform commands can be used with this script

## `mysql.sh`

Deploy MySQL Docker container locally for development

* `scripts/mysql.sh up` - brings up MySQL Docker container locally using `docker-compose.yaml` file in `db/mysql` directory.
* `scripts/mysql.sh down` - brings down MySQL Docker container

## `runtests.sh`

* `scripts/runtests.sh` - run unit tests for driver location producer application

## `tf.sh`

* `scripts/tf.sh tf up -var-file='dev.tfvars'` - deploys the infrastructure
* `scripts/tf.sh tf down -var-file='dev.tfvars'` - tears down the infrastructure

All Terraform commands can be used with this script
