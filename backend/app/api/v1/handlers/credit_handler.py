import random
import string
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import SessionLocal
from app.models.models import UserCredit, CreditPurchase, UserActivityLog, User

def generate_fake_reference():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


# def simulate_purchase(user_id: str, credit_amount: int):
#     db: Session = SessionLocal()
#     try:
#         user_credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
#         if not user_credit:
#             return None, "User not found or has no wallet."

#         # Update balance
#         user_credit.credits_balance += credit_amount
#         user_credit.updated_at = func.now()
#         db.commit()

#         # Insert credit purchase log
#         new_purchase = CreditPurchase(
#             user_id=user_id,
#             credits_added=credit_amount,
#             payment_provider=random.choice(["paypal", "stripe", "test_gateway"]),
#             payment_reference=generate_fake_reference(),
#             created_at=datetime.utcnow()
#         )
#         db.add(new_purchase)
#         db.commit()

#         return user_credit.credits_balance, None
#     finally:
#         db.close()

import random

def generate_ssid():
    return random.randint(100000, 999999)


def simulate_purchase(user_id: str, credit_amount: int):
    db: Session = SessionLocal()
    try:
        user_credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
        if not user_credit:
            return None, "User not found or has no wallet."

        # Update balance
        user_credit.credits_balance += credit_amount
        user_credit.updated_at = func.now()
        db.commit()

        # Insert credit purchase log
        payment_provider = random.choice(["paypal", "stripe", "test_gateway"])
        payment_ref = generate_fake_reference()

        new_purchase = CreditPurchase(
            user_id=user_id,
            credits_added=credit_amount,
            payment_provider=payment_provider,
            payment_reference=payment_ref,
            created_at=datetime.utcnow()
        )
        db.add(new_purchase)
        db.commit()

        # ✅ Find active session (ssid)
        session = db.query(UserActivityLog).filter(
            UserActivityLog.user_id == user_id,
            UserActivityLog.activity_type == "login",
            UserActivityLog.logged_out == None
        ).order_by(UserActivityLog.logged_in.desc()).first()
        ssid = session.ssid if session else generate_ssid()

        # ✅ Add to user_activity_logs
        activity_log = UserActivityLog(
            user_id=user_id,
            activity_type="credit_purchase",
            feature_id=None,  # not tied to a feature
            details=f"Purchased {credit_amount} credits via {payment_provider} (Ref: {payment_ref})",
            ip_address="",  # optionally capture IP from request
            user_agent="",  # optionally capture User-Agent from request
            ssid=ssid,
            created_at=datetime.utcnow()
        )
        db.add(activity_log)
        db.commit()

        return user_credit.credits_balance, None
    finally:
        db.close()