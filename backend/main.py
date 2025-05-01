from fastapi import FastAPI
from app.api.v1.endpoints.auth import auth
from app.api.v1.endpoints import dashboard
from app.core.config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

# FastAPI app
app = FastAPI()

# Example usage of configuration
@app.on_event("startup")
async def startup():
    print(f"Starting with CLIENT_ID: {CLIENT_ID}, CLIENT_SECRET: {CLIENT_SECRET}")

# Include API routes
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])