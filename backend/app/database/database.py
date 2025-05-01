from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base  # Import the declarative base
from app.core.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST, POSTGRES_PORT

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Run this once to create tables (can be done via Alembic later for migrations)
def init_db():
    Base.metadata.create_all(bind=engine)
