#!/bin/bash

DEFAULT_IMAGE="psamsotha/jenkins-docker:latest"
CMD="$1"

printHelp() {
  echo "Usage: jenkins.sh [docker, tf] [subcommand] [args, options]"
  echo "  docker [build, push] [--tag IMAGE_TAG]"
  echo "  tf [up, down, any-tf-command] [args, options]"
}

getDockerImageName() {
  if "$1" == "--tag"; then
    if [ -z "$2" ]; then
      return "$2"
    else
      echo "--tag must have an argument." && exit 1
    fi
  else
    return "$DEFAULT_IMAGE"
  fi
}

buildDockerImage() {
  DOCKER_CMD="$1"
  case "$DOCKER_CMD" in
    "build") shift; docker build -t getDockerImageName $* ./jenkins ;;
    "push") shift; docker push getDockerImageName $*  ;;
    *) echo "Invalid command"; printHelp ;;
  esac
}

runTerraform() {
  WORKDIR="./jenkins"

  if ! type terraform >/dev/null  2>&1 ; then
    echo "Terraform is not installed."
    exit 1
  else
    TF_CMD="$1"
  fi

  case "$TF_CMD" in
    "up" | "UP") shift; terraform -chdir="$WORKDIR" apply $*;;
    "down" | "DOWN") shift; terraform -chdir="$WORKDIR" destroy $*;;
    *) terraform -chdir="$WORKDIR" $*
    ;;
  esac
}

case "$CMD" in
  "-h"|"--help") printHelp && exit 0;;
  "docker") shift; buildDockerImage $* ;;
  "tf") shift; runTerraform $* ;;
  *) echo "Invalid command."; printHelp ;;
esac
