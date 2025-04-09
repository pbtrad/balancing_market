import boto3
import os
import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.ml_models.inference.predict import PredictionService
from datetime import time

router = APIRouter()

lambda_client = boto3.client("lambda", region_name=os.getenv("AWS_REGION", "eu-west-1"))
s3_client = boto3.client("s3")

LAMBDA_FUNCTION_NAME = os.getenv("SCRAPER_LAMBDA_NAME")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")


@router.post("/forecast/trigger_scraper")
def trigger_lambda_scraper():
    """Invoke Lambda function to scrape new data from EirGrid."""
    try:
        response = lambda_client.invoke(FunctionName=LAMBDA_FUNCTION_NAME, InvocationType="Event")
        return {"message": "Scraper Lambda function triggered", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to invoke Lambda: {str(e)}")


@router.post("/forecast/predict")
def predict_forecast(features: list[float], db: Session = Depends(get_db)):
    """Make a real-time forecast prediction using the trained model."""
    service = PredictionService(db)
    prediction = service.predict(np.array(features).reshape(1, -1))
    return {"predicted_value": prediction.tolist()}