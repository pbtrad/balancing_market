import boto3
import os

sagemaker_client = boto3.client("sagemaker")

training_image = os.getenv("SAGEMAKER_TRAINING_IMAGE")
role_arn = os.getenv("SAGEMAKER_ROLE_ARN")
input_data_s3_uri = os.getenv("S3_INPUT_DATA_URI")
output_data_s3_uri = os.getenv("S3_OUTPUT_DATA_URI")

response = sagemaker_client.create_training_job(
    TrainingJobName="balancing-market-forecasting",
    AlgorithmSpecification={
        "TrainingImage": training_image,
        "TrainingInputMode": "File"
    },
    RoleArn=role_arn,
    InputDataConfig=[
        {
            "ChannelName": "train",
            "DataSource": {
                "S3DataSource": {
                    "S3Uri": input_data_s3_uri,
                    "S3DataType": "S3Prefix",
                    "S3DataDistributionType": "FullyReplicated"
                }
            },
            "ContentType": "text/csv"
        }
    ],
    OutputDataConfig={
        "S3OutputPath": output_data_s3_uri
    },
    ResourceConfig={
        "InstanceType": "ml.m5.large",
        "InstanceCount": 1,
        "VolumeSizeInGB": 50
    },
    StoppingCondition={
        "MaxRuntimeInSeconds": 3600
    }
)
print("Training job submitted:", response["TrainingJobArn"])