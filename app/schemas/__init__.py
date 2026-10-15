"""Schema models for the API."""

from .house import (
    HouseFeatures,
    HousePrediction,
    PredictionHistoryResponse,
    PredictionRecordResponse,
)

__all__ = [
    "HouseFeatures",
    "HousePrediction",
    "PredictionHistoryResponse",
    "PredictionRecordResponse",
]
