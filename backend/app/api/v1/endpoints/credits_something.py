from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.models.model import User
from app.dependencies.current_user import get_admin
from sqlalchemy.orm import Session
from app.database.database import get_db

router = APIRouter()

@router.get("/credits")
async def get_credits(db: Session = Depends(get_db),
                       current_user: User = Depends(get_admin)):
    
    return JSONResponse(content={"message": "Welcome to the credits!"})