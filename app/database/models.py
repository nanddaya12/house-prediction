from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    MedInc = Column(Float, nullable=False)
    HouseAge = Column(Float, nullable=False)
    AveRooms = Column(Float, nullable=False)
    AveBedrms = Column(Float, nullable=False)
    Population = Column(Float, nullable=False)
    AveOccup = Column(Float, nullable=False)
    Latitude = Column(Float, nullable=False)
    Longitude = Column(Float, nullable=False)
    predicted_value = Column(Float, nullable=False)
    estimated_price_usd = Column(Float, nullable=False)
    status = Column(String(50), default="completed")
    created_at = Column(DateTime, server_default=func.now(), default=datetime.utcnow)
