#!/bin/bash

set -e
AWS_REGION="eu-west-1"
STACK_PREFIX="balancing-market"
COMPUTE_STACK_NAME="${STACK_PREFIX}-compute"
APPLICATION_STACK_NAME="${STACK_PREFIX}-application"

# Deploy Compute Stack
echo "Deploying Compute Stack..."
aws cloudformation deploy \
  --stack-name $COMPUTE_STACK_NAME \
  --template-file deploy/cloudformation/compute/compute.yml \
  --capabilities CAPABILITY_NAMED_IAM

echo "Compute Stack deployed successfully."

# Deploy Application Stack
echo "Deploying Application Stack..."
aws cloudformation deploy \
  --stack-name $APPLICATION_STACK_NAME \
  --template-file deploy/cloudformation/application/application.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides ComputeStackName=$COMPUTE_STACK_NAME

echo "Application Stack deployed successfully."
