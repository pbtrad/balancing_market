import boto3
import requests
import os
import logging
import json
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    try:
        logger.info("Starting scraper function")
        BUCKET_NAME = os.environ.get("BUCKET_NAME")

        endpoints = {
            "demand": "demandactual",
            "generation": "generationactual",
            "price": "marketprice",
            "imbalance": "imbalancevolume"
        }

        all_data = {}
        for data_type, endpoint in endpoints.items():
            logger.info(f"Fetching {data_type} data")
            response = requests.get(
                "https://www.eirgrid.ie/api/graph-data",
                params={"area": endpoint, "region": "ALL"}
            )
            response.raise_for_status()
            all_data[data_type] = response.json()

        filename = f"market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        logger.info("Saving data to S3")
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"raw/{filename}",
            Body=json.dumps(all_data),
            ContentType="application/json",
        )

        return {"statusCode": 200, "body": json.dumps(f"Data saved to S3: {filename}")}
    except Exception as e:
        logger.error(f"Error in scraper function: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
