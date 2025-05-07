from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL
from app.models.models import Base
from sqlalchemy import text
# Create engine
# engine = create_engine(config.DATABASE_URL, echo=True)

engine = create_engine(
    DATABASE_URL,
    pool_size=500,
    max_overflow=400,
    pool_timeout=60
)

# Create session factory
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

with engine.begin() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS vector"))

# Initialize database (create tables)
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=503, detail="Database service is temporarily unavailable. Please try again later. get_db")
    finally:
        db.close()
