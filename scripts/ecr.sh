#!/bin/bash

read -rp 'Enter AWS account ID: ' ACCOUNT
read -rp 'Enter AWS profile: ' PROFILE
read -rp 'Enter AWS region: ' REGION
read -rp 'Enter Docker context: ' CTX
read -rp 'Enter Dockerfile: ' DOCKERFILE
read -rp 'Enter image name: ' IMAGE

aws --profile "$PROFILE" ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "${ACCOUNT}".dkr.ecr.us-west-2.amazonaws.com
docker build -t "$IMAGE" -f "$DOCKERFILE" "$CTX"
docker tag "${IMAGE}":latest "${ACCOUNT}".dkr.ecr.us-west-2.amazonaws.com/"${IMAGE}":latest
docker push "${ACCOUNT}".dkr.ecr.us-west-2.amazonaws.com/"${IMAGE}":latest
