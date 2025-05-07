from fastapi import FastAPI
from app.api.v1.endpoints import features  # Import features endpoints
from app.api.v1.endpoints import credit  # If credit is part of your endpoints
from app.api.v1.endpoints import oauth  # If oauth is part of your endpoints
from app.database.database import engine  # Import the SQLAlchemy engine
from sqlalchemy import text

# Initialize FastAPI app
app = FastAPI()

# Include the routers for each feature, credit, and oauth
app.include_router(features.router, prefix="/api/v1", tags=["features"])
app.include_router(credit.router, prefix="/api/v1", tags=["credit"])
app.include_router(oauth.router, prefix="/api/v1", tags=["auth"])

# Any other initialization, such as database connection, can also go here

@app.on_event("startup")
def create_vector_extension():
    with engine.connect() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
