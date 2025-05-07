from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core import config
from app.models.models import Base
from sqlalchemy import text
# Create engine
engine = create_engine(config.DATABASE_URL, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize database (create tables)
def init_db():
    Base.metadata.create_all(bind=engine)

def create_vector_extension():
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

def create_vector_schema():
    with engine.connect() as connection:
        connection.execute(text("create schema if not exists vector;"))
