from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.models import User, UserCredit, CreditUsage, UserActivityLog
from app.models.models import UserRole
from sqlalchemy.exc import IntegrityError

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


def add_role(role_name: str, role_level: int):
    session = SessionLocal()
    try:
        if session.query(UserRole).filter_by(role_name=role_name).first():
            return False, "Role already exists."

        new_role = UserRole(role_name=role_name, role_level=role_level)
        session.add(new_role)
        session.commit()
        return True, "Role added successfully."
    except IntegrityError:
        session.rollback()
        return False, "Integrity error. Possibly duplicate or invalid input."
    finally:
        session.close()


def delete_role(role_name: str):
    session = SessionLocal()
    try:
        role = session.query(UserRole).filter_by(role_name=role_name).first()
        if not role:
            return False, "Role not found."

        session.delete(role)
        session.commit()
        return True, "Role deleted successfully."
    finally:
        session.close()


def get_all_roles():
    session = SessionLocal()
    try:
        roles = session.query(UserRole).all()
        return [{"role_name": r.role_name, "role_level": r.role_level} for r in roles]
    finally:
        session.close()
