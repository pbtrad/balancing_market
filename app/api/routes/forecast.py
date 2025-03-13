import boto3
import os
import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.sagemaker.jobs.submit_training_job import submit_training_job
from app.ml_models.inference.predict import PredictionService
from datetime import time

router = APIRouter()

lambda_client = boto3.client("lambda")
s3_client = boto3.client("s3")

LAMBDA_FUNCTION_NAME = os.getenv("SCRAPER_LAMBDA_NAME")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
SAGEMAKER_ROLE_ARN = os.getenv("SAGEMAKER_ROLE_ARN")
SAGEMAKER_TRAINING_IMAGE = os.getenv("SAGEMAKER_TRAINING_IMAGE")


@router.post("/forecast/trigger_scraper")
def trigger_lambda_scraper():
    """Invoke Lambda function to scrape new data from EirGrid."""
    try:
        response = lambda_client.invoke(FunctionName=LAMBDA_FUNCTION_NAME, InvocationType="Event")
        return {"message": "Scraper Lambda function triggered", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to invoke Lambda: {str(e)}")


@router.post("/forecast/train")
def trigger_sagemaker_training():
    """Start a new SageMaker training job."""
    job_name = f"forecast-training-{int(time.time())}"
    response = submit_training_job(
        job_name=job_name,
        training_image=SAGEMAKER_TRAINING_IMAGE,
        role_arn=SAGEMAKER_ROLE_ARN,
        input_data_s3_uri=f"s3://{S3_BUCKET}/input-data/",
        output_data_s3_uri=f"s3://{S3_BUCKET}/output-data/",
    )
    return {"message": "SageMaker training started", "TrainingJobArn": response}


@router.post("/forecast/predict")
def predict_forecast(features: list[float], db: Session = Depends(get_db)):
    """Make a real-time forecast prediction using the trained model."""
    service = PredictionService(db)
    prediction = service.predict(np.array(features).reshape(1, -1))
    return {"predicted_value": prediction.tolist()}