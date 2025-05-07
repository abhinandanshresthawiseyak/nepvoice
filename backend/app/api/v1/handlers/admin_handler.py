from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.models import User, UserCredit, CreditUsage, UserActivityLog

def is_admin(user_id: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user and user.role_level >= 2
    finally:
        db.close()

def delete_user(target_user_id: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == target_user_id).first()
        if not user:
            return False, "User not found."
        db.delete(user)
        db.commit()
        return True, f"User {target_user_id} deleted successfully."
    finally:
        db.close()

def get_all_users_details():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        details = []
        for user in users:
            credits = db.query(UserCredit).filter(UserCredit.user_id == user.id).first()
            activities = db.query(UserActivityLog).filter(UserActivityLog.user_id == user.id).all()
            usages = db.query(CreditUsage).filter(CreditUsage.user_id == user.id).all()

            details.append({
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "role_level": user.role_level,
                "credits_balance": credits.credits_balance if credits else 0,
                "activity_logs": [
                    {
                        "activity_type": log.activity_type,
                        "feature_id": log.feature_id,
                        "details": log.details,
                        "timestamp": log.created_at
                    } for log in activities
                ],
                "credit_usages": [
                    {
                        "feature_id": usage.feature_id,
                        "credits_used": usage.credits_used,
                        "timestamp": usage.created_at
                    } for usage in usages
                ]
            })
        return details
    finally:
        db.close()
