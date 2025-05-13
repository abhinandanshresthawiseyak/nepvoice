from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.database.database import SessionLocal
from app.models.models import Feature, UserCredit, CreditUsage, UserActivityLog, User
from fastapi import Request
def generate_ssid():
    import random
    return random.randint(100000, 999999)

def handle_feature_use(user_id: str, feature_name: str, ip_address: str, user_agent: str,session_id: str = None):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None, "User not found."

        is_admin = user.role_level >= 2

        feature = db.query(Feature).filter(Feature.name == feature_name).first()
        if not feature:
            return None, "Feature not found."

        # Find latest session (ssid) → fallback: generate one
        session = db.query(UserActivityLog).filter(
            UserActivityLog.user_id == user_id,
            UserActivityLog.logged_out == None
        ).order_by(UserActivityLog.logged_in.desc()).first()
        # ssid = session.ssid if session else generate_ssid()
        ssid = session_id if session_id else generate_ssid()
        credit_cost = feature.credit_cost if not is_admin else 0

        if not is_admin and not feature.is_free:
            wallet = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
            if not wallet:
                return None, "User wallet not found."
            if wallet.credits_balance < feature.credit_cost:
                return None, "Insufficient credits."
            wallet.credits_balance -= feature.credit_cost
            wallet.updated_at = func.now()
            db.commit()

        usage = CreditUsage(
            user_id=user_id,
            feature_id=feature.id,
            credits_used=credit_cost,
            created_at=datetime.utcnow()
        )
        db.add(usage)

        log = UserActivityLog(
            user_id=user_id,
            activity_type="feature_use",
            feature_id=feature.id,
            details=f"Used feature: {feature_name}",
            ip_address=ip_address,
            user_agent=user_agent,
            ssid=ssid,
            created_at=datetime.now()
        )
        db.add(log)

        db.commit()

        response = {
            "message": f"Feature '{feature_name}' used successfully.",
            "credits_deducted": credit_cost,
            "ssid": ssid,
        }
        if not is_admin and not feature.is_free:
            wallet = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
            response["remaining_balance"] = wallet.credits_balance

        return response, None

    finally:
        db.close()
