from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import User
from app.dependencies.current_user import get_current_user
from app.utils.api_key import generate_secure_api_key

router = APIRouter()

@router.post("/generate-api-key", summary="Generate API key for the logged-in user")
def generate_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.api_key:
        return {"message": "API key already exists", "api_key": current_user.api_key}

    new_key = generate_secure_api_key()

    # update user row in DB
    db.query(User).filter_by(id=current_user.id).update({"api_key": new_key})
    db.commit()

    updated_user = db.query(User).filter_by(id=current_user.id).first()
    return {"message": "API key generated successfully", "api_key": updated_user.api_key}
