import boto3
import os
import argparse
from app.utils.logging import logger


def upload_to_s3(bucket_name, local_path, s3_prefix=""):
    s3_client = boto3.client("s3")
    for root, _, files in os.walk(local_path):
        for file in files:
            file_path = os.path.join(root, file)
            s3_key = os.path.join(s3_prefix, file).replace("\\", "/")
            logger.info(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
            s3_client.upload_file(file_path, bucket_name, s3_key)


def main():
    parser = argparse.ArgumentParser(description="Upload local data to S3.")
    parser.add_argument("--bucket", required=True, help="S3 bucket name")
    parser.add_argument(
        "--local-path", required=True, help="Local path to the data directory"
    )
    parser.add_argument(
        "--s3-prefix", default="", help="S3 prefix (folder) for the uploaded files"
    )

    args = parser.parse_args()
    upload_to_s3(args.bucket, args.local_path, args.s3_prefix)


if __name__ == "__main__":
    main()
