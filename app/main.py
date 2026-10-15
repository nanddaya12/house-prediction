from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys

# Ensure repository root is in sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import init_db
from app.routers.prediction import router as prediction_router
from app.services.prediction_service import get_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown routines."""
    logger.info("Initializing database schema...")
    init_db()
    logger.info("Pre-warming ML model into memory...")
    get_model()
    logger.info("Application startup completed successfully.")
    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title="House Price Prediction API",
    description="Predict California house values using a machine learning model.",
    version="1.1.0",
    lifespan=lifespan,
)

# Enable CORS for local Streamlit, frontend dev servers, and external callers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
def home():
    return {
        "title": "House Price Prediction API",
        "version": "1.1.0",
        "status": "online",
        "docs_url": "/docs",
    }


@app.get("/health", tags=["General"])
def health():
    """Health check endpoint to verify API and model readiness."""
    model = get_model()
    return {
        "status": "healthy",
        "database": "connected",
        "model_loaded": model is not None,
    }


app.include_router(prediction_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
