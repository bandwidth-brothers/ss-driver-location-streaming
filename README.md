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
    * [Driver Location Producer](#driver-location-producer)


## Setup Python Virtual Environment

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

### Driver Location Producer

* First make sure the [Python virtual environment is set up](#setup-python-virtual-environment).
* Environment variables should be set up for:
    * `GOOGLE_API_KEY`
    
To run the producer program, there needs to be deliveries in the database. Deliveries can be
added using the `app.data.dbdata` module.

```shell
(.venv) $ python -m app.data.dbdata --drivers 2 --custs 10  --orders 10
```

#### Test run the producer

```shell
(.venv) $ python -m app.produce
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

for location in producer.get_driver_locations():
    print(location)

producer.join()
```

The loop will end when there are no more deliveries to process, and the last driver location for the
last delivery has been emitted. Driver locations will be emitted in random order, with all deliveries
being intertwined. To make sure all locations are emitted and that the program doesn't hang, the client
must call `producer.join()`.

[docker]: https://docs.docker.com/get-docker/