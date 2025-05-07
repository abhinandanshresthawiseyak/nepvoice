import random
import string
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import SessionLocal
from app.models.models import UserCredit, CreditPurchase

def generate_fake_reference():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))


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
        new_purchase = CreditPurchase(
            user_id=user_id,
            credits_added=credit_amount,
            payment_provider=random.choice(["paypal", "stripe", "test_gateway"]),
            payment_reference=generate_fake_reference(),
            created_at=datetime.utcnow()
        )
        db.add(new_purchase)
        db.commit()

        return user_credit.credits_balance, None
    finally:
        db.close()
