"""Service layer for ML prediction."""

from .prediction_service import (
    get_model,
    get_prediction_by_id,
    get_prediction_history,
    predict_house_price,
)

__all__ = [
    "predict_house_price",
    "get_model",
    "get_prediction_history",
    "get_prediction_by_id",
]
