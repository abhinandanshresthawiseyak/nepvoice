# app/api/v1/handlers/credit_handler.py

from database.database import database, user_credits, credit_purchases
from sqlalchemy import select, update, insert
from datetime import datetime
import random
import string
from fastapi import HTTPException

def generate_fake_reference():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

async def simulate_credit_purchase(user_id: str, credit_amount: int):
    result = await database.fetch_one(select(user_credits).where(user_credits.c.user_id == user_id))
    if not result:
        raise HTTPException(status_code=404, detail="User not found or has no wallet.")

    new_balance = result["credits_balance"] + credit_amount

    await database.execute(update(user_credits)
        .where(user_credits.c.user_id == user_id)
        .values(credits_balance=new_balance, updated_at=datetime.utcnow())
    )

    await database.execute(insert(credit_purchases).values(
        user_id=user_id,
        credits_added=credit_amount,
        payment_provider=random.choice(["paypal", "stripe", "test_gateway"]),
        payment_reference=generate_fake_reference(),
        created_at=datetime.utcnow()
    ))

    return {
        "message": f"{credit_amount} credits added to user {user_id}.",
        "new_balance": new_balance
    }
