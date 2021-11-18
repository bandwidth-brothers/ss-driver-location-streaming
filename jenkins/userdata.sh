#!/bin/bash

yum install -y docker
service docker start
usermod -a -G docker ec2-user
docker network create jenkins-sonar
docker pull psamsotha/jenkins-docker
docker run -d --net jenkins-sonar \
  -v jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 8080:8080 -p 50000:50000 \
  --name jenkins \
  psamsotha/jenkins-docker:latest
docker pull sonarqube
docker run -d --net jenkins-sonar --name sonarqube -p 9000:9000 sonarqube
