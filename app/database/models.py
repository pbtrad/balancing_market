from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.database import Base
import datetime


class DemandForecast(Base):
    __tablename__ = "demand_forecast"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, unique=True)
    forecasted_demand = Column(Float, nullable=False)  # Predicted demand
    actual_demand = Column(Float, nullable=True)  # Real demand
    error_margin = Column(Float, nullable=True)  # Diff between predicted and actual


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(
        Enum("generator", "supplier", "aggregator", name="participant_type"),
        nullable=False,
    )
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    meters = relationship("MeterPoint", back_populates="participant")


class MeterPoint(Base):
    __tablename__ = "meter_points"

    id = Column(Integer, primary_key=True, index=True)
    mprn = Column(String, unique=True, nullable=False)  # meter point registration no.
    participant_id = Column(Integer, ForeignKey("participants.id"))
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    participant = relationship("Participant", back_populates="meters")
