import boto3
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
if not BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME environment variable is not set")

PREFIX = "raw/"
LOCAL_DIR = os.path.join("app", "data", "raw")

def download_s3_files():
    s3 = boto3.client("s3")

    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)

    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
    for obj in response.get("Contents", []):
        key = obj["Key"]
        filename = os.path.basename(key)
        local_path = os.path.join(LOCAL_DIR, filename)

        print(f"Downloading {key} to {local_path}")
        s3.download_file(BUCKET_NAME, key, local_path)

if __name__ == "__main__":
    download_s3_files()