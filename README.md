# 🏡 California House Price Prediction & Appraisal Platform

An end-to-end Machine Learning web application predicting California housing prices using demographics, spatial coordinates, and property characteristics. Built with **FastAPI**, **SQLAlchemy**, **LightGBM**, and **Streamlit**.

---

## 🏗️ Architecture

```
├── app/
│   ├── main.py                 # FastAPI application & lifespan management
│   ├── database/
│   │   ├── connection.py       # Engine & Sessionmaker
│   │   ├── models.py           # SQLAlchemy PredictionRecord with timestamps
│   │   ├── session.py          # get_db dependency provider
│   │   └── create_database.py  # Database initialization CLI
│   ├── models/
│   │   ├── house_price_model.pkl # Serialized LightGBM model
│   │   └── train_model.py      # Training & evaluation script
│   ├── routers/
│   │   └── prediction.py       # Prediction, history & audit routes
│   ├── schemas/
│   │   └── house.py            # Pydantic validation models
│   └── services/
│       └── prediction_service.py # In-memory cached inference & DB persistence
├── frontend/
│   └── app.py                  # Streamlit dashboard with map & history
├── tests/
│   └── test_api.py             # Automated test suite
└── requirements.txt
```

---

## ⚡ Quickstart

### 1. Environment Setup

Activate your Python virtual environment:
```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. (Optional) Train or Retrain the Model

To train the LightGBM regressor on the California Housing dataset:
```powershell
python -m app.models.train_model
```
Outputs model metrics ($R^2$ and RMSE) and saves `app/models/house_price_model.pkl`.

### 3. Start the FastAPI Backend

```powershell
python -m uvicorn app.main:app --reload --port 8000
```
- API root: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### 4. Start the Streamlit Frontend

In a separate terminal:
```powershell
python -m streamlit run frontend/app.py
```
Opens in your browser at `http://localhost:8501`.

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service metadata and health status |
| `GET` | `/health` | System health check and model loading status |
| `POST` | `/predict/` | Run appraisal on property features and save to DB |
| `GET` | `/predict/history` | Paginated list of historical predictions (`limit`, `offset`) |
| `GET` | `/predict/{id}` | Retrieve a specific prediction record by ID |

### Example Prediction Request:
```bash
curl -X POST "http://127.0.0.1:8000/predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "MedInc": 5.2,
    "HouseAge": 24.0,
    "AveRooms": 5.9,
    "AveBedrms": 1.1,
    "Population": 1450.0,
    "AveOccup": 3.1,
    "Latitude": 34.05,
    "Longitude": -118.25
  }'
```

---

## 🧪 Running Tests

Run the test suite using Python's built-in `unittest`:
```powershell
python -m unittest tests/test_api.py
```

---

## ⚙️ Configuration

Environment variables (optional):
- `DATABASE_URL`: SQLAlchemy connection string (default: `sqlite:///./house_predictions.db`).
- `API_URL`: Backend URL for Streamlit frontend (default: `http://127.0.0.1:8000`).
