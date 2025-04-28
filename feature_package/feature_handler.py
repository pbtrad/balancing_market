import logging
import json
from app.feature_engineering.demand_features import generate_features_for_next_24h
import boto3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event=None, context=None):
    logger.info("Running feature generation Lambda...")

    try:
        features_df = generate_features_for_next_24h()
        
        s3 = boto3.client('s3')
        bucket_name = os.environ['BUCKET_NAME']
        
        for idx, row in features_df.iterrows():
            feature_data = row.to_dict()
            timestamp = feature_data['timestamp']
            
            s3.put_object(
                Bucket=bucket_name,
                Key=f'features/{timestamp}.json',
                Body=json.dumps(feature_data)
            )

        return {
            "statusCode": 200,
            "body": "Feature generation completed successfully."
        }

    except Exception as e:
        logger.exception("Feature generation failed.")
        return {
            "statusCode": 500,
            "body": f"Feature generation failed: {str(e)}"
        } 