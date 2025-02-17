#!/bin/bash

set -e
AWS_REGION="eu-west-1"
STACK_PREFIX="balancing-market"
COMPUTE_STACK_NAME="${STACK_PREFIX}-compute"
APPLICATION_STACK_NAME="${STACK_PREFIX}-application"
ECR_REPO_NAME="${STACK_PREFIX}-app-repository"

# Deploy Compute Stack
echo "Deploying Compute Stack..."
aws cloudformation deploy \
  --stack-name $COMPUTE_STACK_NAME \
  --template-file ./cloudformation/compute/compute.yml \
  --capabilities CAPABILITY_NAMED_IAM

echo "Compute Stack deployed successfully."

# Retrieve ECR Repository URI
ECR_URI=$(aws cloudformation describe-stacks \
  --stack-name $COMPUTE_STACK_NAME \
  --query "Stacks[0].Outputs[?ExportName=='${COMPUTE_STACK_NAME}-ECRRepositoryUri'].OutputValue" \
  --output text)

if [[ -z "$ECR_URI" ]]; then
  echo "Error: Failed to retrieve ECR Repository URI."
  exit 1
fi

echo "ECR Repository URI: $ECR_URI"

# Build and Push Docker Image to ECR
echo "Building Docker Image..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

docker build -t $ECR_REPO_NAME .
docker tag $ECR_REPO_NAME:latest $ECR_URI:latest
docker push $ECR_URI:latest
echo "Docker Image pushed to ECR."

# Deploy Application Stack
echo "Deploying Application Stack..."
aws cloudformation deploy \
  --stack-name $APPLICATION_STACK_NAME \
  --template-file ./cloudformation/application/application.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    ComputeStackName=$COMPUTE_STACK_NAME \
    DockerImageUri=$ECR_URI:latest

echo "Application Stack deployed successfully."
