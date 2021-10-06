# Smoothstack Scrumptious Driver Location Streaming

* [Setup Python Virtual Environment](#setup-python-virtual-environment)
    * [UNIX](#unix)
    * [Windows](#windows)
* [Development](#development)
    * [Setup MySQL Database](#setup-mysql-database)
        * [Start up the Docker container](#start-up-the-docker-container)
        * [Check the connection](#check-the-connection)
        * [Verify setup](#verify-setup)
* [Testing](#testing)
    * [Test Setup](#test-setup)
    * [Run Tests](#run-tests)
* [Production](#production)
* [Application](#application)
    * [Adding Initial Data](#adding-initial-data)
    * [Driver Location Producer](#driver-location-producer)
        * [Run the producer as an application](#run-the-producer-as-an-application)
        * [Consume the producer in an application](#consume-the-producer-in-an-application)
    * [Driver Location Kinesis Consumer](#driver-location-kinesis-consumer)
        * [Setup AWS keys](#setup-aws-keys)
        * [Setup Kinesis stream and Lambda logging consumer](#setup-kinesis-stream-and-lambda-logging-consumer)
        * [Run Kinesis Consumer](#run-kinesis-consumer)
        * [View data streamed to Kinesis](#view-data-streamed-to-kinesis)


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

## Development

### Setup MySQL Database

#### Start up the Docker container

MySQL database is run in a Docker container. You should have [Docker][docker] installed on your development machine.

```shell
$ docker-compose up
```

#### Check the connection

A MySQL container should now be running. You can test that you can connect to it if you have the MySQL client configured

```
$ mysql -h 127.0.0.1 -u smootstack -p
Welcome to the MySQL monitor.  Commands end with ; or \g.
...
mysql>
```

#### Verify setup

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
> and want them re-run, you will need to delete the volumes and run `docker-compose up --build`.
> 
>     $ docker-compose down
>     $ docker volume ls
>     local     ss-driver-location-streaming_mysql_config
>     local     ss-driver-location-streaming_mysql_data
>     $ docker volume rm ss-driver-location-streaming_mysql_config
>     $ docker volume rm ss-driver-location-streaming_mysql_data
>     $ docker-compose up --build

#### Shutdown MySQL Container

```shell
# CTRL-C out of the running container then run
$ docker-compose down
```

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

The [`./runtests.sh`](/runtests.sh) file sets these environment variables.
Individual tests or test directories may be passed to the `runtests.sh` script.
The default is run all tests in the `tests/` directory.

```shell
(.venv) $ ./runtests.sh tests/some_test.py::test_some_function
(.venv) $ ./runtests.sh tests/somedir tests/anotherdir
```

Test files should end with `_test.py`. Tests will be run using an H2 database.


## Production

* First make sure the [Python virtual environment is set up](#setup-python-virtual-environment).
* Environment variables should be set up for:
    * `DATABASE_URL`
    * `DATABASE_USER`
    * `DATABASE_PASSWORD`
    * `GOOGLE_API_KEY`
    
The Google API key should have Google Maps API enabled. There is an `.env` file that contains
default values for these variables. If they are not set externally, these values will be used.
They are only for development and should be used in production.


## Application

* First make sure the [Python virtual environment is set up](#setup-python-virtual-environment).
* Environment variables should be set up for:
    * `GOOGLE_API_KEY`
* See [Production](#production) if running in production.

###  Adding Initial Data

To run the producer or consumer programs, there needs to be deliveries in the database. Deliveries
can be added using the `app.data.dbdata` module.

```shell
(.venv) $ python -m app.data.dbdata --drivers 2 --custs 10  --orders 10
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
Coordinates will be generated based off the directions, and the points will be saved into a file.
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
must call `producer.join()`.


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
      
#### Setup Kinesis stream and Lambda logging consumer

Kinesis and the Lambda logging consumer are set up with Terraform. All the required
Terraform infrastructure code are included in this project. The files are included
in the `./terraform` director. [Terraform][terraform] will need to be installed to
create the required infrastructure.

The working directory will need to be changed to run Terraform commands. That can be
accomplished with the `-chdir` option. There is a `tf.sh` script that will add this
option automatically. There are also shortcut commands `up` and `down` which are
equivalent to `apply` and `destroy`, respectively. You can also use all the other
`terraform` commands with this script. Examples:

* `./tf.sh init` - Initialize Terraform project. This should be called before any of
                   the following commands
* `./tf.sh up` - Create infrastructure (type 'yes' when prompted). Same as `terraform applu
* `./tf.sh down` - Destroy infrastructure (type 'yes' when prompted)
* `./tf.sh plan` - Plan infrastructure

#### Run Kinesis Consumer

First make sure there is some [initial data](#adding-initial-data).

The consumer application will consume the data from the driver location producer and
then stream it to Kinesis. The consumer can be run with the following Python program

```shell
(.venv) $ python -m app.consume [--help]
```

The following options are available for the program:

* `-n`, `--stream-name` - name of the Kinesis stream
* `-l`, `--log` - log level (default `INFO`)
* `-r`, `--records-per-request` - number of records to send for each Kinesis request (default 100)
* `-d`, `--delay` - delay (in seconds) between Kinesis requests (default 0.3)
* `-v`, `--verbose` - same as `--log VERBOSE`

#### View data streamed to Kinesis

The consumer of the Kinesis stream is a Lambda function that just logs all the records.
The logs will get sent out to CloudWatch. To view the logs:

1. Go the [Lambda Home Page](https://console.aws.amazon.com/lambda/home#/functions)
2. Select the function (default "DriverLocationConsumerFunction")
3. Select the "Monitor" tab
4. Click the "View logs in CloudWatch" button. This should open a new CloudWatch window.
5. Select the latest log stream. You should now see all the driver location data logs.


[docker]: https://docs.docker.com/get-docker/
[aws-cli]: https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html
[terraform]: https://www.terraform.io/downloads.html