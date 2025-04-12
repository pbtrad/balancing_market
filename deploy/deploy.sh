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

# Retrieve Compute Stack Outputs
DATA_BUCKET_NAME=$(aws cloudformation list-exports \
  --query "Exports[?Name=='${COMPUTE_STACK_NAME}-DataBucketName'].Value" \
  --output text)

LAMBDA_ROLE_ARN=$(aws cloudformation list-exports \
  --query "Exports[?Name=='${COMPUTE_STACK_NAME}-LambdaRoleArn'].Value" \
  --output text)

if [[ -z "$DATA_BUCKET_NAME" || -z "$LAMBDA_ROLE_ARN" ]]; then
  echo "Error: Missing required values from Compute Stack outputs."
  exit 1
fi

echo "Compute Stack Outputs:"
echo "DataBucketName: $DATA_BUCKET_NAME"
echo "LambdaRoleArn: $LAMBDA_ROLE_ARN"

# Upload Lambda package to S3
echo "Uploading Lambda package to S3..."
aws s3 cp eirgrid_scraper.zip "s3://${DATA_BUCKET_NAME}/lambda/eirgrid_scraper.zip"

# Deploy Application Stack
echo "Deploying Application Stack..."
aws cloudformation deploy \
  --stack-name $APPLICATION_STACK_NAME \
  --template-file deploy/cloudformation/application/application.yml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    ComputeStackName=$COMPUTE_STACK_NAME

echo "Application Stack deployed successfully."
