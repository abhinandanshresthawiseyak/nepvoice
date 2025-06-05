# app/dependencies/api_key_user.py

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import User

def get_user_from_api_key(
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.api_key == x_api_key).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")
    return user
