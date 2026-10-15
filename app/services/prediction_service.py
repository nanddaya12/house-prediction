import logging
from pathlib import Path
from typing import List, Optional, Tuple

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.database.models import PredictionRecord
from app.schemas.house import HouseFeatures

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "house_price_model.pkl"
FEATURE_COLUMNS = [
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
]

_cached_model = None


def train_and_save_model():
    """Train a California housing model using HistGradientBoostingRegressor and persist it."""
    logger.info("Training new model on California housing dataset...")
    from sklearn.datasets import fetch_california_housing
    from sklearn.ensemble import HistGradientBoostingRegressor

    housing = fetch_california_housing(as_frame=True)
    features = housing.data[FEATURE_COLUMNS]
    target = housing.target

    model = HistGradientBoostingRegressor(
        max_iter=300,
        learning_rate=0.05,
        max_leaf_nodes=31,
        random_state=42,
    )
    model.fit(features, target)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    logger.info("Model successfully trained and saved to %s", MODEL_PATH)
    return model


def get_model():
    """Return the cached in-memory ML model, loading it if not yet loaded."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    if MODEL_PATH.exists():
        try:
            logger.info("Loading ML model from %s", MODEL_PATH)
            _cached_model = joblib.load(MODEL_PATH)
            return _cached_model
        except Exception as exc:
            logger.warning("Failed to load existing model file (%s). Retraining...", exc)

    _cached_model = train_and_save_model()
    return _cached_model


def predict_house_price(data: HouseFeatures, db: Optional[Session] = None) -> dict:
    """Predict the house price using the cached ML model and log to DB if session provided."""
    model = get_model()
    payload = data.model_dump() if hasattr(data, "model_dump") else data.dict()
    input_data = pd.DataFrame([payload])[FEATURE_COLUMNS]

    raw_prediction = float(model.predict(input_data)[0])
    # Ensure prediction is non-negative
    prediction = max(0.0, raw_prediction)
    price_in_dollars = round(prediction * 100000, 2)

    result = {
        "predicted_value": round(prediction, 3),
        "estimated_price_usd": price_in_dollars,
        "currency": "USD",
        "prediction_id": None,
    }

    # Record prediction to database
    owns_session = False
    session = db
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        record = PredictionRecord(
            MedInc=payload["MedInc"],
            HouseAge=payload["HouseAge"],
            AveRooms=payload["AveRooms"],
            AveBedrms=payload["AveBedrms"],
            Population=payload["Population"],
            AveOccup=payload["AveOccup"],
            Latitude=payload["Latitude"],
            Longitude=payload["Longitude"],
            predicted_value=result["predicted_value"],
            estimated_price_usd=result["estimated_price_usd"],
            status="completed",
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        result["prediction_id"] = record.id
    except Exception as exc:
        session.rollback()
        logger.error("Failed to persist prediction record to database: %s", exc)
    finally:
        if owns_session:
            session.close()

    return result


def get_prediction_history(
    db: Session, limit: int = 50, offset: int = 0
) -> Tuple[int, List[PredictionRecord]]:
    """Retrieve paginated prediction records ordered by latest first."""
    total = db.query(PredictionRecord).count()
    records = (
        db.query(PredictionRecord)
        .order_by(PredictionRecord.created_at.desc(), PredictionRecord.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return total, records


def get_prediction_by_id(db: Session, prediction_id: int) -> Optional[PredictionRecord]:
    """Retrieve a single prediction record by ID."""
    return db.query(PredictionRecord).filter(PredictionRecord.id == prediction_id).first()


if __name__ == "__main__":
    house = HouseFeatures(
        MedInc=5.0,
        HouseAge=20.0,
        AveRooms=6.0,
        AveBedrms=1.0,
        Population=1000.0,
        AveOccup=3.0,
        Latitude=34.05,
        Longitude=-118.25,
    )
    result = predict_house_price(house)
    print("Prediction successful!")
    print(result)
