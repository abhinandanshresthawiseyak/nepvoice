from fastapi import Request, HTTPException
from app.database.database import SessionLocal
from app.models.models import UserActivityLog, User

# def get_logged_in_user(request: Request) -> User:
#     ssid = request.cookies.get("user_id")
#     if not ssid:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     db = SessionLocal()
#     try:
#         session = db.query(UserActivityLog).filter(
#             UserActivityLog.ssid == ssid,
#             UserActivityLog.logged_out == None
#         ).order_by(UserActivityLog.logged_in.desc()).first()

#         if not session:
#             raise HTTPException(status_code=401, detail="Session expired or invalid")

#         user = db.query(User).filter(User.id == session.user_id).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         return user
#     finally:
#         db.close()


# from fastapi import Request, HTTPException
# from app.database.database import SessionLocal
# from app.models.models import User

# def get_logged_in_user(request: Request) -> User:
#     user_id = request.session.get("user_id")
#     if not user_id:
#         raise HTTPException(status_code=401, detail="Not authenticated")

#     db = SessionLocal()
#     try:
#         user = db.query(User).filter(User.id == user_id).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#         return user
#     finally:
#         db.close()



from fastapi import Request, HTTPException
from app.database.database import SessionLocal
from app.models.models import User

def get_logged_in_user(request: Request) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    finally:
        db.close()
