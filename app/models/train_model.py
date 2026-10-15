from pathlib import Path

import joblib
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from app.services.prediction_service import FEATURE_COLUMNS, MODEL_PATH


def main() -> None:
    housing = fetch_california_housing(as_frame=True)
    features = housing.data[FEATURE_COLUMNS]
    target = housing.target

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
    )
    model = HistGradientBoostingRegressor(
        max_iter=300,
        learning_rate=0.05,
        max_leaf_nodes=31,
        random_state=42,
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Training rows: {len(x_train):,}")
    print(f"Validation rows: {len(x_test):,}")
    print(f"Validation RMSE: {rmse:.4f} (units of $100,000)")
    print(f"Validation R²: {r2:.4f}")
    print(f"Saved trained model: {MODEL_PATH}")


if __name__ == "__main__":
    main()
