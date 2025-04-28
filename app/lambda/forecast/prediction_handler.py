import logging
import json
import boto3
from datetime import datetime, timedelta
from app.database.database import get_db
from app.ml_models.inference.predict import PredictionService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event=None, context=None):
    logger.info("Running prediction Lambda...")

    try:
        s3 = boto3.client("s3")
        bucket_name = context.client_context.custom["bucket_name"]

        features = []
        for i in range(24):
            timestamp = (datetime.now() + timedelta(hours=i)).strftime("%Y%m%d%H")
            try:
                response = s3.get_object(
                    Bucket=bucket_name, Key=f"features/{timestamp}.json"
                )
                feature_data = json.loads(response["Body"].read())
                features.append(feature_data)
            except s3.exceptions.NoSuchKey:
                logger.warning(f"No features found for timestamp {timestamp}")
                continue

        if not features:
            raise Exception("No features found for prediction")

        db = get_db()
        service = PredictionService(db)

        for feature_data in features:
            timestamp = datetime.strptime(feature_data["timestamp"], "%Y%m%d%H")
            # Add some kind prediction logic here using the feature data maybe

        return {"statusCode": 200, "body": "Prediction completed successfully."}

    except Exception as e:
        logger.exception("Prediction failed.")
        return {"statusCode": 500, "body": f"Prediction failed: {str(e)}"}
