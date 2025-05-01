from datetime import datetime
import pytz
from app.core.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT
from sqlalchemy.orm import sessionmaker
import uuid
from sqlalchemy import create_engine

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(
    DATABASE_URL,
    pool_size=500,
    max_overflow=400,
    pool_timeout=60
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

