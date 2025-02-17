import boto3
import argparse
import sys
from app.utils.logging import logger


def submit_training_job(
    job_name, training_image, role_arn, input_data_s3_uri, output_data_s3_uri
):
    sagemaker_client = boto3.client("sagemaker")

    try:
        response = sagemaker_client.create_training_job(
            TrainingJobName=job_name,
            AlgorithmSpecification={
                "TrainingImage": training_image,
                "TrainingInputMode": "File",
            },
            RoleArn=role_arn,
            InputDataConfig=[
                {
                    "ChannelName": "train",
                    "DataSource": {
                        "S3DataSource": {
                            "S3Uri": input_data_s3_uri,
                            "S3DataType": "S3Prefix",
                            "S3DataDistributionType": "FullyReplicated",
                        }
                    },
                    "ContentType": "text/csv",
                }
            ],
            OutputDataConfig={"S3OutputPath": output_data_s3_uri},
            ResourceConfig={
                "InstanceType": "ml.m5.large",
                "InstanceCount": 1,
                "VolumeSizeInGB": 50,
            },
            StoppingCondition={"MaxRuntimeInSeconds": 3600},
        )
        logger.info("Training job submitted successfully!")
        logger.info(f"Training Job ARN: {response['TrainingJobArn']}")
    except Exception as e:
        logger.error(f"Error submitting training job: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Submit a SageMaker training job.")
    parser.add_argument("--job-name", required=True, help="Name of the training job")
    parser.add_argument(
        "--training-image", required=True, help="URI of the training Docker image"
    )
    parser.add_argument("--role-arn", required=True, help="IAM role ARN for SageMaker")
    parser.add_argument(
        "--input-data-s3-uri", required=True, help="S3 URI for input data"
    )
    parser.add_argument(
        "--output-data-s3-uri", required=True, help="S3 URI for output data"
    )

    args = parser.parse_args()

    submit_training_job(
        job_name=args.job_name,
        training_image=args.training_image,
        role_arn=args.role_arn,
        input_data_s3_uri=args.input_data_s3_uri,
        output_data_s3_uri=args.output_data_s3_uri,
    )


if __name__ == "__main__":
    main()
