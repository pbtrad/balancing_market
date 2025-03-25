import os
import json
import logging
from datetime import datetime
import requests

try:
    import boto3
except ImportError:
    boto3 = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEMO_ENDPOINTS = {
    "bm_025_shadow_prices": "BM-025",
    "bm_026_imbalance_prices": "BM-026",
    "bm_084_fx_rates": "BM-084",
    "bm_095_costs": "BM-095",
}

BASE_URL = "https://reports.sem-o.com/api/v1/dynamic"


def fetch_semo_data(report_code, start_time, end_time):
    params = {
        "StartTime": f">={start_time}",
        "EndTime": f"<={end_time}",
        "sort_by": "StartTime",
        "order_by": "ASC",
        "Jurisdiction": "All",
        "page": 1,
        "page_size": 5000,
    }

    url = f"{BASE_URL}/{report_code}"
    logger.info(f"Fetching {report_code} data")
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def save_to_s3(bucket_name, key, data):
    if not boto3:
        raise RuntimeError("boto3 is not available.")
    s3 = boto3.client("s3")
    logger.info(f"Uploading {key} to S3 bucket {bucket_name}")
    s3.put_object(
        Bucket=bucket_name,
        Key=key,
        Body=json.dumps(data),
        ContentType="application/json",
    )


def handler(event=None, context=None, save_local=False):
    bucket_name = os.environ.get("BUCKET_NAME")
    today = datetime.utcnow().strftime("%Y-%m-%d")
    filename_prefix = f"semo_{today.replace('-', '')}"

    start_time = today + "T00:00"
    end_time = today + "T23:59"

    all_data = {}
    for name, code in SEMO_ENDPOINTS.items():
        try:
            data = fetch_semo_data(code, start_time, end_time)
            all_data[name] = data
        except Exception as e:
            logger.error(f"Error fetching {code}: {e}")

    if save_local or not bucket_name:
        # Save to local file for local testing
        os.makedirs("data", exist_ok=True)
        filepath = f"data/{filename_prefix}.json"
        with open(filepath, "w") as f:
            json.dump(all_data, f, indent=2)
        logger.info(f"Saved SEMO data locally to {filepath}")
    else:
        # Save to S3
        key = f"raw/{filename_prefix}.json"
        save_to_s3(bucket_name, key, all_data)

    return {"status": "ok", "records_fetched": list(all_data.keys())}


if __name__ == "__main__":
    handler(save_local=True)
