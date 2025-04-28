import boto3
import os
import json
import pandas as pd
from datetime import datetime, timedelta, timezone

def generate_features_for_next_24h():
    """Read today's data from S3 and generate time-based features"""

    s3 = boto3.client("s3")
    bucket_name = os.environ["S3_BUCKET_NAME"]
    prefix = "raw/"

    today_str = datetime.now(timezone.utc).strftime("%Y%m%d")

    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    timestamps = []

    for obj in response.get("Contents", []):
        key = obj["Key"]
        if today_str not in key or not key.endswith(".json"):
            continue

        file_obj = s3.get_object(Bucket=bucket_name, Key=key)
        raw_json = json.loads(file_obj["Body"].read())

        for record in raw_json.values():
            timestamp = datetime.now(timezone.utc)
            timestamps.append(timestamp)

    if not timestamps:
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        timestamps = [now + timedelta(hours=i) for i in range(24)]

    df = pd.DataFrame(
        {
            "hour": [t.hour for t in timestamps],
            "day_of_week": [t.weekday() for t in timestamps],
            "is_weekend": [t.weekday() >= 5 for t in timestamps],
        }
    )

    return df
