# Scripts

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

### Deploy Docker Container Locally

* `scripts/mysql.sh up` - brings up MySQL Docker container locally using `docker-compose.yaml` file in `db/mysql` directory.
* `scripts/mysql.sh down` - brings down MySQL Docker container

## `runtests.sh`

* `scripts/runtests.sh` - run unit tests for driver location producer application

## `tf.sh`

* `scripts/tf.sh tf up -var-file='dev.tfvars'` - deploys the infrastructure
* `scripts/tf.sh tf down -var-file='dev.tfvars'` - tears down the infrastructure

All Terraform commands can be used with this script
