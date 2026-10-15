import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.models import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./house_predictions.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
