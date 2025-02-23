import logging
from sqlalchemy.orm import Session
from datetime import datetime
from app.database.models import MarketPrediction
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self, db: Session):
        self.db = db

    def create_prediction(
        self,
        timestamp: datetime,
        predicted_demand_mw: float,
        predicted_price: Optional[float] = None,
        predicted_imbalance_mw: Optional[float] = None,
        model_version: str = "1.0.0",
    ) -> MarketPrediction:
        """Create a new prediction record"""
        prediction = MarketPrediction(
            timestamp=timestamp,
            predicted_demand_mw=predicted_demand_mw,
            predicted_price=predicted_price or 0.0,
            predicted_imbalance_mw=predicted_imbalance_mw or 0.0,
            model_version=model_version,
        )

        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        logger.info(f"Created new prediction: {prediction}")
        return prediction

    def update_actual_values(
        self,
        prediction_id: int,
        actual_demand_mw: Optional[float] = None,
        actual_price: Optional[float] = None,
        actual_imbalance_mw: Optional[float] = None,
    ) -> Optional[MarketPrediction]:
        """Update prediction with actual values"""

        prediction = self.db.get(MarketPrediction, prediction_id)
        if not prediction:
            logger.warning(f"Prediction with ID {prediction_id} not found.")
            return None

        if actual_demand_mw is not None:
            prediction.actual_demand_mw = actual_demand_mw
            prediction.demand_error = actual_demand_mw - prediction.predicted_demand_mw

        if actual_price is not None:
            prediction.actual_price = actual_price
            prediction.price_error = actual_price - (prediction.predicted_price or 0.0)

        if actual_imbalance_mw is not None:
            prediction.actual_imbalance_mw = actual_imbalance_mw
            prediction.imbalance_error = actual_imbalance_mw - (
                prediction.predicted_imbalance_mw or 0.0
            )

        self.db.commit()
        self.db.refresh(prediction)

        logger.info(f"Updated prediction {prediction_id} with actual values.")
        return prediction

    def get_recent_predictions(self, limit: int = 24) -> List[MarketPrediction]:
        """Get most recent predictions"""
        predictions = (
            self.db.query(MarketPrediction)
            .order_by(MarketPrediction.timestamp.desc())
            .limit(limit)
            .all()
        )

        logger.info(f"Fetched {len(predictions)} recent predictions.")
        return predictions
