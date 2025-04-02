import os
import json
import boto3
import requests
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

EIRGRID_API_URL = "https://www.eirgrid.ie/api/graph-data"

# Active endpoint for scraping demand only
ENDPOINTS = {
    "demand": "demandactual"
}

# Endpointsfor future use
# ENDPOINTS = {
#     "demandactual": "demand_actual",
#     "demandforecast": "demand_forecast",
#     "windactual": "wind_actual",
#     "windforecast": "wind_forecast",
#     "fuelmix": "fuel_mix",
#     "co2emission": "co2_emission",
#     "co2intensity": "co2_intensity",
#     "interconnector": "interconnector",
# }

def fetch_data_from_eirgrid(endpoints: dict) -> dict:
    """
    Fetch JSON data from multiple EirGrid areas.
    """
    date_str = datetime.utcnow().strftime("%d %b %Y")
    all_data = {}

    for label, area in endpoints.items():
        logger.info(f"Fetching {label} data from EirGrid")
        try:
            response = requests.get(
                EIRGRID_API_URL,
                params={"area": area, "region": "ALL", "date": date_str},
                timeout=10
            )
            response.raise_for_status()
            all_data[label] = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch {label}: {str(e)}")

    return all_data


def upload_to_s3(bucket_name: str, data: dict, region: str = "eu-west-1") -> str:
    """
    Upload collected data as a JSON file to S3.
    """
    s3 = boto3.client("s3", region_name=region)
    filename = f"raw/market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    logger.info(f"Uploading raw data to S3 at {filename}")

    s3.put_object(
        Bucket=bucket_name,
        Key=filename,
        Body=json.dumps(data),
        ContentType="application/json",
    )

    return filename


def handler(event=None, context=None):
    logger.info("Starting EirGrid scraper Lambda")

    try:
        BUCKET_NAME = os.environ["BUCKET_NAME"]
        AWS_REGION = os.environ.get("AWS_REGION", "eu-west-1")

        data = fetch_data_from_eirgrid(ENDPOINTS)
        s3_key = upload_to_s3(BUCKET_NAME, data, region=AWS_REGION)

        return {
            "statusCode": 200,
            "body": json.dumps(f"Data saved to S3: {s3_key}")
        }

    except Exception as e:
        logger.error(f"Scraper failed: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }