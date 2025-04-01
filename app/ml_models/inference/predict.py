import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from app.database.models import Forecast, ActualData, ForecastEvaluation, MarketTypeEnum
import joblib

from app.feature_engineering.demand_features import generate_features_for_next_24h

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self, db: Session):
        self.db = db

    def create_forecast(
        self,
        forecast_time: datetime,
        market_type: MarketTypeEnum,
        forecast_type: str,
        value: float,
        source: str = "LSTM",
        region: str = "ALL",
    ) -> Forecast:
        """Create a new forecast record"""
        forecast = Forecast(
            forecast_time=forecast_time,
            market_type=market_type,
            forecast_type=forecast_type,
            value=value,
            source=source,
            region=region,
        )

        self.db.add(forecast)
        self.db.commit()
        self.db.refresh(forecast)

        logger.info(f"Created new forecast: {forecast}")
        return forecast

    def update_actual_values(
        self,
        actual_time: datetime,
        market_type: MarketTypeEnum,
        data_type: str,
        value: float,
        region: str = "ALL",
    ) -> ActualData:
        """Update actual values after market data is available"""
        actual_data = ActualData(
            actual_time=actual_time,
            market_type=market_type,
            data_type=data_type,
            value=value,
            region=region,
        )

        self.db.add(actual_data)
        self.db.commit()
        self.db.refresh(actual_data)

        logger.info(f"Added actual data: {actual_data}")
        return actual_data

    def evaluate_forecast(
        self,
        forecast_time: datetime,
        market_type: MarketTypeEnum,
        model_name: str = "LSTM",
    ) -> Optional[ForecastEvaluation]:
        """Evaluate forecast accuracy by comparing it to actual values"""
        forecast = (
            self.db.query(Forecast)
            .filter(
                Forecast.forecast_time == forecast_time,
                Forecast.market_type == market_type,
            )
            .first()
        )

        actual = (
            self.db.query(ActualData)
            .filter(
                ActualData.actual_time == forecast_time,
                ActualData.market_type == market_type,
            )
            .first()
        )

        if not forecast or not actual:
            logger.warning(
                f"No matching forecast or actual data found for {forecast_time}."
            )
            return None

        error = abs(actual.value - forecast.value)
        evaluation = ForecastEvaluation(
            model_name=model_name,
            market_type=market_type,
            forecast_time=forecast_time,
            actual_value=actual.value,
            forecast_value=forecast.value,
            error=error,
            mae=error,
            rmse=error**2,  # Placeholder for RMSE calculation
        )

        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)

        logger.info(f"Evaluated forecast: {evaluation}")
        return evaluation

    def get_recent_forecasts(
        self, market_type: MarketTypeEnum, limit: int = 24
    ) -> List[Forecast]:
        """Retrieve most recent forecasts"""
        forecasts = (
            self.db.query(Forecast)
            .filter(Forecast.market_type == market_type)
            .order_by(Forecast.forecast_time.desc())
            .limit(limit)
            .all()
        )

        logger.info(f"Fetched {len(forecasts)} recent forecasts.")
        return forecasts

    def run_forecast_for_next_24h(self):
        model = joblib.load("models/demand_forecast_model.pkl")
        future_features = generate_features_for_next_24h()
        predictions = model.predict(future_features)

        for i, value in enumerate(predictions):
            forecast_time = datetime.utcnow().replace(
                minute=0, second=0, microsecond=0
            ) + timedelta(hours=i)
            self.create_forecast(
                forecast_time=forecast_time,
                market_type=MarketTypeEnum.DAM,
                forecast_type="DEMAND",
                value=value,
            )
