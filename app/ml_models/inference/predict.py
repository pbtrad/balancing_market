import logging
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from app.database.models import (DemandForecast, PriceForecast, 
                               GenerationForecast, ImbalanceForecast, 
                               ForecastEvaluation, MarketTypeEnum, ForecastTypeEnum)
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
        forecast_type: ForecastTypeEnum,
        value: float,
        source: str = "LSTM",
        region: str = "ALL",
    ):
        """Create a new forecast record"""
        if forecast_type == ForecastTypeEnum.DEMAND:
            forecast = DemandForecast(
                forecast_time=forecast_time,
                market_type=market_type,
                predicted_demand_mw=value,
                source=source,
                region=region,
            )
        elif forecast_type == ForecastTypeEnum.PRICE:
            forecast = PriceForecast(
                forecast_time=forecast_time,
                market_type=market_type,
                predicted_price=value,
                source=source,
                region=region,
            )
        
        self.db.add(forecast)
        self.db.commit()
        self.db.refresh(forecast)
        return forecast

    def update_actual_values(
        self,
        actual_time: datetime,
        market_type: MarketTypeEnum,
        forecast_type: ForecastTypeEnum,
        value: float,
        region: str = "ALL",
    ) -> Optional[DemandForecast | PriceForecast | GenerationForecast | ImbalanceForecast]:
        """Update actual values after market data is available"""
        
        # Get existing forecast
        if forecast_type == ForecastTypeEnum.DEMAND:
            forecast = self.db.query(DemandForecast).filter(
                DemandForecast.forecast_time == actual_time,
                DemandForecast.market_type == market_type
            ).first()
            if forecast:
                forecast.actual_demand_mw = value
                forecast.demand_error = abs(forecast.predicted_demand_mw - value)
        
        if forecast:
            self.db.commit()
            self.db.refresh(forecast)
        
        return forecast

    def evaluate_forecast(
        self,
        forecast_time: datetime,
        market_type: MarketTypeEnum,
        forecast_type: ForecastTypeEnum,
        model_name: str = "LSTM",
    ) -> Optional[ForecastEvaluation]:
        """Evaluate forecast accuracy by comparing it to actual values"""
        if forecast_type == ForecastTypeEnum.DEMAND:
            forecast = (
                self.db.query(DemandForecast)
                .filter(
                    DemandForecast.forecast_time == forecast_time,
                    DemandForecast.market_type == market_type,
                )
                .first()
            )
            if not forecast or forecast.actual_demand_mw is None:
                logger.warning(f"No matching forecast or actual data found for {forecast_time}.")
                return None
            error = abs(forecast.actual_demand_mw - forecast.predicted_demand_mw)
            actual_value = forecast.actual_demand_mw
            forecast_value = forecast.predicted_demand_mw


        evaluation = ForecastEvaluation(
            model_name=model_name,
            market_type=market_type,
            forecast_time=forecast_time,
            actual_value=actual_value,
            forecast_value=forecast_value,
            error=error,
            mae=error,
            rmse=error**2,
        )

        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def get_recent_forecasts(
        self, 
        market_type: MarketTypeEnum, 
        forecast_type: ForecastTypeEnum,
        limit: int = 24
    ) -> List[DemandForecast | PriceForecast | GenerationForecast | ImbalanceForecast]:
        """Retrieve most recent forecasts"""
        if forecast_type == ForecastTypeEnum.DEMAND:
            model = DemandForecast
        elif forecast_type == ForecastTypeEnum.PRICE:
            model = PriceForecast
        
        forecasts = (
            self.db.query(model)
            .filter(model.market_type == market_type)
            .order_by(model.forecast_time.desc())
            .limit(limit)
            .all()
        )
        
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
