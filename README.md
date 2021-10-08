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
| customer_address      |
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
19 rows in set (0.00 sec)
```

>**NOTE:** With this `docker-compose` setup, persistent volumes will be setup to save data.
> The SQL init scripts will only be run one time. If you make any changes to the scripts
> and want them re-run, you will need to delete the volumes and run `docker-compose` up again.
> 
>     $ docker volume ls
>     local     ss-driver-location-streaming_mysql_config
>     local     ss-driver-location-streaming_mysql_data
>     $ docker volume rm ss-driver-location-streaming_mysql_config
>     $ docker volume rm ss-driver-location-streaming_mysql_data

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
    
The Google API key should have Google Maps API enabled.

[docker]: https://docs.docker.com/get-docker/