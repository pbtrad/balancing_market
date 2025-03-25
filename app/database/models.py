from sqlalchemy import Column, Index, Integer, Float, String, DateTime, Enum, ForeignKey, TypeDecorator
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

from app.database.database import Base

class StringEnum(TypeDecorator):
    impl = String

    def __init__(self, enumclass, *args, **kwargs):
        self._enumclass = enumclass
        super().__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        return value.value if value else None

    def process_result_value(self, value, dialect):
        return self._enumclass(value) if value else None
    
class MarketTypeEnum(PyEnum):
    DAM = "DAM"  # Day-Ahead Market
    IDM = "IDM"  # Intra-Day Market
    BM = "BM"    # Balancing Market


class ForecastTypeEnum(PyEnum):
    DEMAND = "DEMAND"
    PRICE = "PRICE"
    GENERATION = "GENERATION"
    IMBALANCE = "IMBALANCE"


### BASE FORECAST MODEL ###
class BaseForecast(Base):
    """ Abstract Base Model for Forecasts """
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow, nullable=False)  # Time of forecast creation
    forecast_time = Column(DateTime, index=True, nullable=False)  # Time the forecast is for
    market_type = Column(StringEnum(MarketTypeEnum), nullable=False)  # DAM, IDM, BM
    region = Column(String, nullable=False, default="ALL")  # Market region
    source = Column(String, nullable=False)  # Model used

    
### DEMAND FORECAST ###
class DemandForecast(BaseForecast):
    """ Forecasted & Actual Demand in MW """
    __tablename__ = "demand_forecasts"

    predicted_demand_mw = Column(Float, nullable=False)
    actual_demand_mw = Column(Float, nullable=True)
    demand_error = Column(Float, nullable=True)  # Difference between predicted & actual demand

    def __repr__(self):
        return f"<DemandForecast {self.forecast_time}: {self.predicted_demand_mw} MW>"


### PRICE FORECAST ###
class PriceForecast(BaseForecast):
    """ Forecasted & Actual Market Prices in €/MWh """
    __tablename__ = "price_forecasts"

    predicted_price = Column(Float, nullable=False)
    actual_price = Column(Float, nullable=True)
    price_error = Column(Float, nullable=True)  # Diff between predicted & actual price

    def __repr__(self):
        return f"<PriceForecast {self.forecast_time}: {self.predicted_price} €/MWh>"


### GENERATION FORECAST ###
class GenerationForecast(BaseForecast):
    """ Forecasted & Actual Generation in MW """
    __tablename__ = "generation_forecasts"

    predicted_generation_mw = Column(Float, nullable=False)
    actual_generation_mw = Column(Float, nullable=True)
    generation_error = Column(Float, nullable=True)  # Difference between predicted & actual generation

    def __repr__(self):
        return f"<GenerationForecast {self.forecast_time}: {self.predicted_generation_mw} MW>"


### IMBALANCE FORECAST ###
class ImbalanceForecast(BaseForecast):
    """ Forecasted & Actual Imbalance in MW """
    __tablename__ = "imbalance_forecasts"

    predicted_imbalance_mw = Column(Float, nullable=False)
    actual_imbalance_mw = Column(Float, nullable=True)
    imbalance_error = Column(Float, nullable=True)  # Difference between predicted & actual imbalance

    def __repr__(self):
        return f"<ImbalanceForecast {self.forecast_time}: {self.predicted_imbalance_mw} MW>"


### FORECAST EVALUATION METRICS ###
class ForecastEvaluation(Base):
    """
    Evaluation of Forecast Performance.
    Used for ML model comparison (e.g., Mean Absolute Error, RMSE).
    """
    __tablename__ = "forecast_evaluations"
    __table_args__ = (
        Index("idx_forecast_time_type", "forecast_time", "forecast_type"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    forecast_type = Column(Enum(ForecastTypeEnum), nullable=False)
    model_name = Column(String, nullable=False)
    forecast_time = Column(DateTime, nullable=False)
    actual_value = Column(Float, nullable=False)
    forecast_value = Column(Float, nullable=False)
    error = Column(Float, nullable=False)
    mae = Column(Float, nullable=False)
    rmse = Column(Float, nullable=False)
    forecast_history = relationship("ForecastHistory", back_populates="forecast_evaluation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ForecastEvaluation {self.forecast_time} - {self.model_name}: Error {self.error}>"


### RELATIONSHIPS (OPTIONAL) ###
class ForecastHistory(Base):
    """
    Store historical forecasts for analysis.
    Links a forecast entry to its evaluation.
    """
    __tablename__ = "forecast_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    forecast_id = Column(Integer, ForeignKey("forecast_evaluations.id"), nullable=False)
    forecast_evaluation = relationship("ForecastEvaluation", back_populates="forecast_history")

    def __repr__(self):
        return f"<ForecastHistory ForecastID: {self.forecast_id}>"

