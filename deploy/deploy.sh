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

# Retrieve Compute Stack Name
COMPUTE_STACK_OUTPUT=$(aws cloudformation describe-stacks \
  --stack-name $COMPUTE_STACK_NAME \
  --query "Stacks[0].StackName" \
  --output text)

if [[ -z "$COMPUTE_STACK_OUTPUT" ]]; then
  echo "Error: Failed to retrieve Compute Stack Name."
  exit 1
fi

echo "Compute Stack Name: $COMPUTE_STACK_OUTPUT"

# Deploy Application Stack
echo "Deploying Application Stack..."
aws cloudformation deploy \
  --stack-name $APPLICATION_STACK_NAME \
  --template-file deploy/cloudformation/application/application.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides ComputeStackName=$COMPUTE_STACK_OUTPUT

echo "Application Stack deployed successfully."

