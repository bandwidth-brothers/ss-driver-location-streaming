#!/bin/bash

yum install -y docker
service docker start
usermod -a -G docker ec2-user
docker network create jenkins-sonar
docker pull jenkins/jenkins:lts-jdk11
docker run -d --net jenkins-sonar -v jenkins_home:/var/jenkins_home \
       -p 8080:8080 -p 50000:50000 -p 8000:8000 --name jenkins \
       jenkins/jenkins:lts-jdk11
docker pull sonarqube
docker run -d --net jenkins-sonar --name sonarqube -p 9000:9000 sonarqube
