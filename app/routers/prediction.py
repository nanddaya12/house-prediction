from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.house import (
    HouseFeatures,
    HousePrediction,
    PredictionHistoryResponse,
    PredictionRecordResponse,
)
from app.services.prediction_service import (
    get_prediction_by_id,
    get_prediction_history,
    predict_house_price,
)

router = APIRouter(prefix="/predict", tags=["House Price Prediction"])


@router.post("/", response_model=HousePrediction, status_code=status.HTTP_200_OK)
def predict(data: HouseFeatures, db: Session = Depends(get_db)):
    """Predict house value and store record in database."""
    return predict_house_price(data, db=db)


@router.get("/history", response_model=PredictionHistoryResponse)
def history(
    limit: int = Query(50, ge=1, le=200, description="Max number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    db: Session = Depends(get_db),
):
    """Retrieve historical prediction records."""
    total, items = get_prediction_history(db=db, limit=limit, offset=offset)
    return {"total": total, "items": items}


@router.get("/{prediction_id}", response_model=PredictionRecordResponse)
def get_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """Retrieve a single prediction record by ID."""
    record = get_prediction_by_id(db=db, prediction_id=prediction_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prediction record {prediction_id} not found.",
        )
    return record
