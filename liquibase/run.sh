#!/bin/bash

print_usage() {
  echo "Usage: liquibase/run.sh [local]"
  echo "  Using the 'local' options requires LIQUIBASE_DOCKER_NETWORK"
  echo "  to be set. This option is used for development with the MySQL"
  echo "  Docker container that is created with the mysql.sh script. The"
  echo "  network should be called 'mysql_scrumptious_db'. Look for"
  echo "  'Creating network' when running 'scripts/mysql.sh up'."
}

if [[ "$1" == "local" ]]; then
  if [[ -z "${LIQUIBASE_DOCKER_NETWORK}" ]]; then
    echo "LIQUIBASE_DOCKER_NETWORK environment variable not set."
    echo
    print_usage
    echo
    exit 1
  fi
  LOCAL=true
fi

if [[ "$(docker images -q liquibase-mysql 2> /dev/null)" == "" ]]; then
  echo "Docker image 'liquibase-mysql' does not exist. Run liquibase/build.sh"
  exit 0;
fi

if [[ "$LOCAL" == true ]]; then
  docker run -it --rm \
    -v "$(pwd)"/liquibase/changelog:/liquibase/changelog \
    -v "$(pwd)"/liquibase/conf.d:/liquibase/conf.d \
    -v "$(pwd)"/liquibase/liquibase.properties:/liquibase/liquibase.properties \
    --name liquibase \
    --network "${LIQUIBASE_DOCKER_NETWORK}" \
    liquibase-mysql bash
else
  docker run -it --rm \
    -v "$(pwd)"/liquibase/changelog:/liquibase/changelog \
    -v "$(pwd)"/liquibase/conf.d:/liquibase/conf.d \
    -v "$(pwd)"/liquibase/liquibase.properties:/liquibase/liquibase.properties \
    --name liquibase \
    liquibase-mysql bash
fi
