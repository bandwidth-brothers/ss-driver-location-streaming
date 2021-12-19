#!/bin/bash

export CLASSPATH='./db/h2/lib/*'
export ENV_FILE='./tests/test.env'

TESTS_DIRS="./tests"

if [[ -n "$1" ]]; then
  TESTS_DIRS="$*"
fi

rm ./tmp/data/db.mv.db 2> /dev/null
rm ./tmp/data/db.trace.db 2> /dev/null
java -jar db/h2/h2-mysql-functions.jar jdbc:h2:./tmp/data/db
python -m tests.init_db
coverage run -m pytest "$TESTS_DIRS" && coverage report -m
