import os
import json
import boto3
import requests
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# EirGrid API endpoints to fetch
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

ENDPOINTS = {
    "demandactual": "demand_actual",
    "demandforecast": "demand_forecast",
}

EIRGRID_API_URL = "https://www.eirgrid.ie/api/graph-data"


def fetch_data_from_eirgrid():
    """
    Fetch JSON data from multiple EirGrid areas.
    """
    date_str = datetime.utcnow().strftime("%d %b %Y")
    all_data = {}

    for area, label in ENDPOINTS.items():
        logger.info(f"Fetching {label} data from EirGrid")
        try:
            response = requests.get(
                EIRGRID_API_URL,
                params={"area": area, "region": "ALL", "date": date_str},
            )
            response.raise_for_status()
            all_data[label] = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch {label}: {str(e)}")

    return all_data


def upload_to_s3(bucket_name: str, data: dict):
    """
    Upload collected data as a JSON file to S3.
    """
    s3 = boto3.client("s3")
    filename = f"raw/market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    logger.info(f"Uploading raw data to S3 at {filename}")
    s3.put_object(
        Bucket=bucket_name,
        Key=filename,
        Body=json.dumps(data),
        ContentType="application/json",
    )


def handler(event=None, context=None):
    logger.info("Starting EirGrid scraper")

    try:
        BUCKET_NAME = os.environ["BUCKET_NAME"]
        data = fetch_data_from_eirgrid()

        # Upload full raw data to S3
        upload_to_s3(BUCKET_NAME, data)

        return {
            "statusCode": 200,
            "body": json.dumps("EirGrid data scraped and uploaded to S3"),
        }

    except Exception as e:
        logger.error(f"Scraper failed: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
