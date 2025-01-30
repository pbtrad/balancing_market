from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from app.database.database import Base
import datetime

class DemandForecast(Base):
    __tablename__ = "demand_forecast"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, unique=True)
    forecasted_demand = Column(Float, nullable=False)  # Predicted demand
    actual_demand = Column(Float, nullable=True)  # Real demand
    error_margin = Column(Float, nullable=True) # Diff between predicted and actual

