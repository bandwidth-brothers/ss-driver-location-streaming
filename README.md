# Smoothstack Scrumptious Driver Location Streaming

## Documents

* [Scripts (helper scripts)](./scripts/README.md)
* [Terraform (infrastructure)](./terraform/README.md)
* [Jenkins (CI/CD)](./jenkins/README.md)
* [Spark (streaming)](./spark/README.md)
* [Liquibase (database management)](./liquibase/README.md)
* [TODOs](./TODO.md)

## Table of Contents

* [Setup Python Virtual Environment](#setup-python-virtual-environment)
    * [UNIX](#unix)
    * [Windows](#windows)
* [Development Database](#development-database)
    * [Setup MySQL Database](#setup-mysql-database)
        * [Start up the Docker container](#start-up-the-docker-container)
        * [Check the connection](#check-the-connection)
        * [Verify setup](#verify-setup)
* [Production Setup](#production-setup)
* [Infrastructure](#infrastructure)
    * [Deploying the Infrastructure](#deploying-the-infrastructure)
    * [Destroy Infrastructure](#destroying-the-infrastructure)
* [Application](#application)
    * [Adding Initial Data](#adding-initial-data)
    * [Driver Location Producer](#driver-location-producer)
        * [Run the producer as an application](#run-the-producer-as-an-application)
        * [Consume the producer in an application](#consume-the-producer-in-an-application)
    * [Driver Location Kinesis Consumer](#driver-location-kinesis-consumer)
        * [Setup AWS keys](#setup-aws-keys)
        * [Run Kinesis Consumer](#run-kinesis-consumer)
        * [View data streamed to Kinesis](#view-data-streamed-to-kinesis)
    * [Spark Streaming](#spark-streaming)
* [Testing](#testing)
    * [Test Setup](#test-setup)
    * [Run Tests](#run-tests)


## Setup Python Virtual Environment

Before running the programs, either in development or production, the Python
virtual environment should set up and dependencies installed. This project was
created with Python 3.9.

### UNIX
```shell
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt

# To deactivate the virtual env run
(.venv) $ deactivate
$
```

### Windows

```shell
C:\> python -m venv .venv
C:\> .\.venv\Scripts\activate.bat
(.venv) C:\> pip install -r requirements.txt

# To deactivate the virtual env run
(.venv) C:\> deactivate
C:\>
```

## Development Database

A MySQL development database may be set up with Docker Compose. An `.env` file is used
for required environment variables.

### Start up the Docker container

MySQL database is run in a Docker container. You should have [Docker][docker] installed on your development machine.

```shell
$ scripts/mysql.sh up
```

### Check the connection

A MySQL container should now be running. You can test that you can connect to it if you have the MySQL client configured

```
$ mysql -h 127.0.0.1 -u smootstack -p
Welcome to the MySQL monitor.  Commands end with ; or \g.
...
mysql>
```

### Verify setup

Make sure the schema is set up correctly

```
mysql> use scrumptious;
Database changed
mysql> show tables;
+-----------------------+
| Tables_in_scrumptious |
+-----------------------+
| address               |
| admin                 |
| category              |
| cuisine               |
| customer              |
| delivery              |
| driver                |
| menuitem              |
| menuitem_category     |
| menuitem_order        |
| menuitem_tag          |
| order                 |
| owner                 |
| payment               |
| restaurant            |
| restaurant_cuisine    |
| tag                   |
| user                  |
+-----------------------+
18 rows in set (0.00 sec)
```

>**NOTE:** With this `docker-compose` setup, persistent volumes will be setup to save data.
> The SQL init scripts will only be run one time. If you make any changes to the scripts
> and want them re-run, you will need to delete the volumes and run `scripts/mysql.sh up --build`.
> 
>     $ scripts/mysql.sh down
>
> and want them re-run, you will need to delete the volumes and run `docker-compose` up again.
> 
>     $ docker volume ls
>     local     ss-driver-location-streaming_mysql_config
>     local     ss-driver-location-streaming_mysql_data
>     $ docker volume rm ss-driver-location-streaming_mysql_config
>     $ docker volume rm ss-driver-location-streaming_mysql_data
>     $ docker-compose up --build


### Shutdown MySQL Container

```shell
# CTRL-C out of the running container then run
$ scripts/mysql.sh down
```

## Production Setup

In a production environment, the following should be done for the producer application:

* First make sure the [Python virtual environment is set up](#setup-python-virtual-environment).
* Environment variables should be set up for:
    * `DATABASE_URL`
    * `DATABASE_USER`
    * `DATABASE_PASSWORD`
    * `GOOGLE_API_KEY`
    
The Google API key should have Google Maps API enabled. There is an `.env` file that contains
default values for these variables. If they are not set externally, these values will be used.
They are only for development and should not be used in production.


## Infrastructure

### Spark Docker on ECS

Spark is run as a Docker container and is deployed to ECS. The infrastructure is deployed with Terraform and CloudFormation.
The following are steps to build the Docker image:

1. `cd` to `./spark` directory
2. Run `docker build --tag <full-tag> .`
3. Run `docker push <full-tag>`

>`<full-tag>` should be in the format `<repository>/<image-name>:<version>`

### Deploying the Infrastructure

Kinesis and Spark are set up with Terraform. All the required Terraform infrastructure
code is included in this project. The files are located in the `./terraform` directory.
[Terraform][terraform] will need to be installed to create the required infrastructure.

The working directory will need to be changed to run Terraform commands. That can be
accomplished with the `-chdir` option. There is a `tf.sh` script that will add this
option automatically. There are also shortcut commands `up` and `down` which are
equivalent to `apply` and `destroy`, respectively. You can also use all the other
`terraform` commands with this script. Examples:

* `./tf.sh init` - Initialize Terraform project. This should be called before any of
                   the following commands
* `./tf.sh up` - Create infrastructure (type 'yes' when prompted). Same as `terraform apply`
* `./tf.sh down` - Destroy infrastructure (type 'yes' when prompted). Same as `terraform destroy`
* `./tf.sh plan` - Plan infrastructure

#### Terraform Variables

A few variables are required to deploy the infrastructure

* `spark_docker_image` - the full tag of the spark docker image built previously
* `aws_region` - the AWS region to deploy to
* `key_name` - the keypair name for EC2 SSH access
* `kinesis_shaed_count` (optional) - the number of Kinesis shards (default 3)
* `ec2_type` (optional) - the EC2 type (default t3.medium)
* `with_lambda_consumer` (optional) - whether to include Lambda consumer (default true)

These variables can be put into a `.tfvars` file and pass through the command line
when deploying the infrastructure. The file is relative to the `./terraform` directory.

```shell
$ ./tf.sh up -var-file='dev.tfvars'
```

#### Example .tfvars file

```shell
spark_docker_image = "my-repo/ss-spark-kinesis-streaming:latest"
key_name = "my-keypair"
aws_region = "us-west-2"
with_lambda_consumer = false
```

### Destroying the Infrastructure

```shell
$ ./tf.sh down -var-file='dev.tfvars'
```

>**Note:** When destroying the infrastructure, the internet gateway will not be able to
> be destroyed because of the IP address associated with the EC2 instance. You will
> need to manually destroy the EC2 by going to the AWS console and manually
> deleting the Auto Scaling Group. Don't delete the EC2. Deleting the ASG will
> automatically terminate the EC2


## Application

* First make sure the [Python virtual environment is set up](#setup-python-virtual-environment).
* Environment variables should be set up for:
    * `GOOGLE_API_KEY`
* See [Production Setup](#production-setup) if running in production.

###  Adding Initial Data

To run the producer or consumer programs, there needs to be deliveries in the database. Deliveries
can be added using the `app.data` module.

```shell
(.venv) $ python -m app.data --drivers 2 --custs 10  --orders 10
```

Deliveries are dependent on there also being customers, restaurants and orders. Those
can also be created with the program.

### Driver Location Producer

First make sure there is some [initial data](#adding-initial-data). Then you can either
run the producer as an application or consume the data from another application.

#### Run the producer as an application

```shell
(.venv) $ python -m app.produce [--help]
...
INFO:root:No file tmp/points/CF939A82461A45BC9700A85B7C1C13F1-6-points.txt. Will make an API call to get points.
INFO:root:delivery: 6, points: 675
INFO:root:All deliveries complete.
INFO:root:{
    "A3B2E8FE01344C649A1704E91A5DB541": 1202,
    "F367F266777447FDB2794BEC8FB26F3B": 1035,
    "5CA0741ED4664AADBA8D4CD8B2A0E158": 1445,
    "CF939A82461A45BC9700A85B7C1C13F1": 3424
}
INFO:root:total pings: 7106
```

When the producer is first run, Google Maps API calls will be made to get directions for a delivery.
Coordinates will be generated based off the directions, and the points generated will be saved into a file.
On the next run, if no deliveries have been added to the database since the previous run, the coordinate
data will be retrieved from these files, and no API calls will need to be made for the deliveries.

#### Consume the producer in an application

The producer has a generator function that can be consumed like an Iterable.

```python
from app.produce.producer import DriverLocationProducer

producer = DriverLocationProducer()
producer.start()
producer.join()

for location in producer.get_driver_locations():
    print(location)
```

The loop will end when there are no more deliveries to process, and the last driver location for the
last delivery has been emitted. Driver locations will be emitted in random order, with all deliveries
being intertwined. To make sure all locations are emitted and that the program doesn't hang, the client
should call `producer.join()`.


### Driver Location Kinesis Consumer

#### Setup AWS keys

To be able to stream the driver location data to Kinesis, you will need to have an AWS account, set up
the [AWS CLI][aws-cli] on your machine, and set up AWS access key ID and the secret access key. There
are two ways to do this:

* With environment variables. The following three variables shoule be set:
    * `AWS_ACCESS_KEY_ID`
    * `AWS_SECRED_ACCESS_KEY`
    * `AWS_DEFAULT_REGION`
* Use the AWS CLI or manually edit the `~/.aws/xxx` files. With the CLI, run `aws configure`,
  and you will be prompted to set up the keys and region. To manually edit the config files, The two
  below files should have the following details:
    * `~/.aws/credentials`:
      ```
      [default]
      aws_access_key_id = <your-access-key-id>
      aws_secret_access_key = <your-secret-access-key>
       ```
    * `~/.aws/config`:
      ```
      [default]
      region = us-west-2
      output = json
      ```
#### Run Kinesis Consumer

First make sure there is some [initial data](#adding-initial-data).

The consumer application will consume the data from the driver location producer and
then stream it to Kinesis. The consumer can be run with the following Python program

```shell
(.venv) $ python -m app.consume.kinesis [--help]
```

The following options are available for the program:

* `-n`, `--stream-name` - name of the Kinesis stream
* `-l`, `--log` - log level (default `INFO`)
* `-r`, `--records-per-request` - number of records to send for each Kinesis request (default 100)
* `-d`, `--delay` - delay (in seconds) between Kinesis requests (default 0.2)
* `-v`, `--verbose` - same as `--log VERBOSE`
* `--producer-max-threads` - max threads for producer thread pool
* `--producer-buffer-size` - max size of internal queue
* `--producer-no-api-key` - if there is no Google Maps API key, points files must be present
* `--producer-delay` - producer delay, in seconds, for each location into buffer (default 0.0)

#### View data streamed to Kinesis

To view the streamed data, you can opt to launch a Lambda logging consumer that will log
records to CloudWatch. To add the consumer, use the `with_lambda_consumer` to the `.tfvars` file.
To view the logs:

1. Go the [Lambda Home Page](https://console.aws.amazon.com/lambda/home#/functions)
2. Select the function (default "DriverLocationConsumerFunction")
3. Select the "Monitor" tab
4. Click the "View logs in CloudWatch" button. This should open a new CloudWatch window.
5. Select the latest log stream. You should now see all the driver location data logs.


## Spark Streaming

The Spark streaming program will ingest location data from the Kinesis stream and
will print the data to the console. After running the program, you will want to start
[streaming the data to Kinesis](#run-kinesis-consumer).

### SSH Into EC2 and Run from Cluster

The streaming program is built into the Docker container. You can SSH into the EC2 instance
and then go into the Docker container and run the script. You will need to go
into the AWS console and get the public IP, or the public DNS of the EC2 instance.

1. `ssh -i <path-to-pem-file> ec2-user@<ec2-public-ip-or-dns>`
2. `docker ps` to get the spark container id
3. `docker exec -it <container-id> bash`
4. `work/runstream.sh`

### Run Locally from Docker Container

The streaming program is included in this project. You can start a local Spark container
and run the program, passing the master URL as a parameter. You will need to go to the
AWS console and get the public IP, or the public DNS of the EC2 instance.

1. `cd` to `./spark` directory
2. Run `docker-compose up`
3. `docker ps` to ge the spark container id
4. `docker exec -it <container-id> bash`
5. `work/runstream.sh --master 'spark://<ec2-ip-or-dns>:7077`

Passing the `--master` will run the spark program on the Spark cluster in ECS.

## Testing

### Test Setup

Make sure the [Python virtual environment is set up](#setup-python-virtual-environment).
Make sure Java runtime is installed and `JAVA_HOME` environment variable is set up.
Test files should end with `_test.py`. Tests will be run using an H2 database.

### Run tests

```shell
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ ./runtests.sh
```

To use H2, the tests require two environment variables, `ENV_FILE` and `CLASSPATH`.

* `ENV_FILE` - the `.env` file used for environment variables.
* `CLASSPATH` - the Java classpath to find classes required for the JVM

The [`./runtests.sh`](/scripts/runtests.sh) file sets these environment variables.
Individual tests or test directories may be passed to the `runtests.sh` script.
The default is run all tests in the `tests/` directory.

```shell
(.venv) $ ./runtests.sh tests/some_test.py::test_some_function
(.venv) $ ./runtests.sh tests/somedir tests/anotherdir
```

Test files should end with `_test.py`. Tests will be run using an H2 database.


[docker]: https://docs.docker.com/get-docker/
[aws-cli]: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
[terraform]: https://www.terraform.io/downloads.html
