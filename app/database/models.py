from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class MarketTypeEnum(Enum):
    DAY_AHEAD = "Day-Ahead Market"
    INTRADAY = "Intraday Market"
    BALANCING = "Balancing Market"

class Forecast(Base):
    """
    Forecast model to store price, demand, and generation forecasts.
    """
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, index=True, default=datetime.now(datetime.UTC))  # Forecast creation time
    forecast_time = Column(DateTime, index=True, nullable=False)  # Time the forecast is for
    market_type = Column(Enum(MarketTypeEnum), nullable=False)  # DAM, IDM, BM
    forecast_type = Column(String, nullable=False)  # "Price", "Demand", "Generation"
    region = Column(String, nullable=False, default="ALL")  # Ireland, NI
    source = Column(String, nullable=False)  # Model used (e.g., "LSTM", "XGBoost")
    value = Column(Float, nullable=False)  # Forecasted value

    def __repr__(self):
        return f"<Forecast {self.forecast_time} - {self.forecast_type}: {self.value}>"

class ActualData(Base):
    """
    Actual recorded values for model evaluation.
    """
    __tablename__ = "actual_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    actual_time = Column(DateTime, index=True, nullable=False)  # Time the actual data was recorded
    market_type = Column(Enum(MarketTypeEnum), nullable=False)
    data_type = Column(String, nullable=False)  # "Price", "Demand", "Generation"
    region = Column(String, nullable=False, default="ALL")
    value = Column(Float, nullable=False)  # Actual recorded value

    def __repr__(self):
        return f"<ActualData {self.actual_time} - {self.data_type}: {self.value}>"

class ForecastEvaluation(Base):
    """
    Model evaluation results comparing forecasted vs actual values.
    """
    __tablename__ = "forecast_evaluation"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_name = Column(String, nullable=False)  # LSTM, XGBoost, ARIMA
    market_type = Column(Enum(MarketTypeEnum), nullable=False)
    forecast_time = Column(DateTime, nullable=False)
    actual_value = Column(Float, nullable=False)
    forecast_value = Column(Float, nullable=False)
    error = Column(Float, nullable=False)  # Absolute error
    mae = Column(Float, nullable=False)  # Mean Absolute Error
    rmse = Column(Float, nullable=False)  # Root Mean Squared Error

    def __repr__(self):
        return f"<ForecastEvaluation {self.forecast_time} - Model: {self.model_name} Error: {self.error}>"
