import logging
import json
from datetime import datetime, timedelta
import os
from app.database.database import get_db
from app.database.models import DemandForecast, MarketTypeEnum, ForecastTypeEnum

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def fallback_prediction(features):
    predictions = []
    for feature in features:
        hour = int(feature.get('hour', 0))
        is_weekend = feature.get('is_weekend', False)
        
        base_load = 3500  
        
        # Time of day factors (just a somewhat calculated estimate)
        if 0 <= hour < 5:  # Night (low demand)
            time_factor = 0.7
        elif 5 <= hour < 9:  # Morning ramp-up
            time_factor = 0.9 + (hour - 5) * 0.1
        elif 9 <= hour < 17:  # Daytime
            time_factor = 1.2
        elif 17 <= hour < 21:  # Evening peak
            time_factor = 1.3
        else:  # Late evening
            time_factor = 1.0 - (hour - 21) * 0.1
        
        # Weekend adjustment
        weekend_factor = 0.85 if is_weekend else 1.0
        
        # Calculate predicted demand
        predicted_demand = base_load * time_factor * weekend_factor
        
        predictions.append(predicted_demand)
    
    return predictions

def create_forecast(db, forecast_time, market_type, forecast_type, value):
    """Create forecast using SQLAlchemy ORM"""
    try:
        if forecast_type == "DEMAND":
            forecast = DemandForecast(
                market_type=market_type,
                forecast_time=forecast_time,
                predicted_demand_mw=value
            )
            db.add(forecast)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        return False

def handler(event=None, context=None):
    logger.info("Running prediction Lambda...")

    try:
        # Generate features for next 24 hours
        features = []
        for i in range(24):
            # Generate timestamps
            timestamp = (datetime.now() + timedelta(hours=i))
            timestamp_str = timestamp.strftime("%Y%m%d%H")
            
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            is_weekend = day_of_week >= 5
            
            feature_data = {
                "timestamp": timestamp_str,
                "hour": hour,
                "day_of_week": day_of_week,
                "is_weekend": is_weekend
            }
            features.append(feature_data)
            logger.info(f"Created basic features for timestamp {timestamp_str}")

        # Get db session
        try:
            db = get_db()
            logger.info("Connected to database successfully")
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            db = None

        logger.info(f"Making predictions for {len(features)} timestamps")
        demand_predictions = fallback_prediction(features)
        
        saved_count = 0
        for i, prediction in enumerate(demand_predictions):
            feature_data = features[i]
            timestamp_str = feature_data["timestamp"]
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d%H")
            
            # Round prediction to nearest whole number
            prediction_value = round(float(prediction))
            
            logger.info(f"Prediction for {timestamp}: {prediction_value} MW")
            
            if db:
                if create_forecast(
                    db,
                    forecast_time=timestamp,
                    market_type=MarketTypeEnum.DAM,
                    forecast_type=ForecastTypeEnum.DEMAND,
                    value=prediction_value
                ):
                    saved_count += 1

        return {
            "statusCode": 200, 
            "body": f"Successfully predicted demand for {len(demand_predictions)} hours, saved {saved_count} to database"
        }

    except Exception as e:
        logger.exception("Prediction failed.")
        return {"statusCode": 500, "body": f"Prediction failed: {str(e)}"}
