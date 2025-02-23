import boto3
import requests
import os
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    try:
        logger.info("Starting scraper function")

        BUCKET_NAME = os.environ.get("BUCKET_NAME")
        logger.info(f"Using bucket: {BUCKET_NAME}")

        api_url = "https://www.eirgrid.ie/api/graph-data"

        logger.info("Fetching data from API")
        response = requests.get(
            api_url, params={"area": "demandactual", "region": "ALL"}
        )
        response.raise_for_status()

        data = response.json()
        filename = "raw_data.json"

        logger.info("Saving data to S3")
        s3 = boto3.client("s3")
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=f"raw/{filename}",
            Body=json.dumps(data),
            ContentType="application/json",
        )

        logger.info(f"Data successfully saved to S3: {filename}")
        return {"statusCode": 200, "body": json.dumps(f"Data saved to S3: {filename}")}

    except Exception as e:
        error_msg = f"Error in scraper function: {str(e)}"
        logger.error(error_msg)
        return {"statusCode": 500, "body": json.dumps({"error": error_msg})}
