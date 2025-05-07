from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.models.models import User
from app.dependencies.current_user import get_admin
from sqlalchemy.orm import Session
from app.database.database import get_db

router = APIRouter()

@router.get("/credits")
async def get_credits(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    users = db.query(User).all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
        }
        for user in users
    ]
