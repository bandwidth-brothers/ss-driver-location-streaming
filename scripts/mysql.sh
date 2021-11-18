#!/bin/bash

print_help() {
  echo "Usage: mysql.sh [up, down]"
}

if [[ $# -ne 1 ]]; then
  print_help
  exit 1
fi

CMD="$1"
if [[ "$CMD" != "up" && "$CMD" != "down" ]]; then
  print_help
  exit 1
fi

cd db/mysql || exit1

docker-compose "$CMD"
