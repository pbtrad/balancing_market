from fastapi import APIRouter, HTTPException
from typing import List

from app.ml_models.inference import predict

router = APIRouter()


@router.post("/predict")
def predict_demand(features: List[float]):
    if not features or len(features) == 0:
        raise HTTPException(status_code=400, detail="No input features provided.")

    try:
        prediction = predict(features)
        forecasted_demand = float(prediction[0])
        return {"forecast": forecasted_demand}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
