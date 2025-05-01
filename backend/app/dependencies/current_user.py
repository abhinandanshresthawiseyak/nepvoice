from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.database.database import get_db
from starlette.requests import Request
from app.utils.error_messages import user_not_found, unauthorized_access, unauthenticated


def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_email = 'user@global.com'
    
    if not user_email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=unauthenticated())

    user = db.query(User).filter(User.email == user_email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=user_not_found())

    return user


def get_admin(request: Request, db: Session = Depends(get_db)):
    user_name = request.session.get('username') 
    # print(user_name)
    if not user_name:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=unauthenticated())

    user = db.query(User).filter(User.name == user_name).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=user_not_found())

    if user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=unauthorized_access())

    return user
