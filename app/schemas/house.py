from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class HouseFeatures(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "MedInc": 5.0,
                "HouseAge": 25.0,
                "AveRooms": 5.8,
                "AveBedrms": 1.05,
                "Population": 1200.0,
                "AveOccup": 3.0,
                "Latitude": 34.05,
                "Longitude": -118.25,
            }
        }
    )

    MedInc: float = Field(
        ...,
        gt=0.0,
        le=50.0,
        description="Median income in block group (in tens of thousands of USD, e.g. 5.0 = $50,000)",
    )
    HouseAge: float = Field(
        ...,
        ge=1.0,
        le=120.0,
        description="Median house age in years",
    )
    AveRooms: float = Field(
        ...,
        gt=0.5,
        le=50.0,
        description="Average number of rooms per household",
    )
    AveBedrms: float = Field(
        ...,
        gt=0.1,
        le=20.0,
        description="Average number of bedrooms per household",
    )
    Population: float = Field(
        ...,
        gt=1.0,
        le=100000.0,
        description="Population in block group",
    )
    AveOccup: float = Field(
        ...,
        gt=0.1,
        le=50.0,
        description="Average number of household members",
    )
    Latitude: float = Field(
        ...,
        ge=32.0,
        le=43.0,
        description="Latitude coordinate (California range: ~32.0 to 43.0)",
    )
    Longitude: float = Field(
        ...,
        ge=-125.0,
        le=-114.0,
        description="Longitude coordinate (California range: ~-125.0 to -114.0)",
    )


class HousePrediction(BaseModel):
    predicted_value: float = Field(..., description="Predicted median house value in units of $100,000")
    estimated_price_usd: float = Field(..., description="Estimated house price in USD")
    currency: str = Field(default="USD", description="Currency of estimated price")
    prediction_id: Optional[int] = Field(default=None, description="Database record ID")


class PredictionRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float
    predicted_value: float
    estimated_price_usd: float
    status: str
    created_at: Optional[datetime] = None


class PredictionHistoryResponse(BaseModel):
    total: int
    items: List[PredictionRecordResponse]
