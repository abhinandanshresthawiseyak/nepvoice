from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core import config
from app.models.models import Base

# Create engine
engine = create_engine(config.DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize database (create tables)
def init_db():
    Base.metadata.create_all(bind=engine)
