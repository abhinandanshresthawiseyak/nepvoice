from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import select, update, insert
from app.database.database import database
from app.models.models import features, user_credits, credit_usage, user_activity_logs

# Shared logic handler for feature use
async def handle_feature_use(user_id: str, feature_name: str, request):
    # Find the feature
    feature = await database.fetch_one(select(features).where(features.c.name == feature_name))
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found.")

    is_free = feature["is_free"]
    credit_cost = feature["credit_cost"]
    feature_id = feature["id"]

    # For free features, just log the usage and return
    if is_free:
        await log_feature_use(user_id, feature_id, 0, feature_name, request)
        return {"message": f"Free feature '{feature_name}' used successfully."}

    # For paid features, check user's credit balance
    wallet = await database.fetch_one(select(user_credits).where(user_credits.c.user_id == user_id))
    if not wallet or wallet["credits_balance"] < credit_cost:
        raise HTTPException(status_code=402, detail="Insufficient credits.")

    new_balance = wallet["credits_balance"] - credit_cost
    # Update the user's credits after feature use
    await database.execute(
        update(user_credits)
        .where(user_credits.c.user_id == user_id)
        .values(credits_balance=new_balance, updated_at=datetime.utcnow())
    )

    # Log feature use
    await log_feature_use(user_id, feature_id, credit_cost, feature_name, request)

    return {
        "message": f"Paid feature '{feature_name}' used successfully.",
        "credits_deducted": credit_cost,
        "remaining_balance": new_balance
    }

# Helper function to log feature usage
async def log_feature_use(user_id, feature_id, credits_used, feature_name, request):
    # Log in credit_usage table
    await database.execute(insert(credit_usage).values(
        user_id=user_id,
        feature_id=feature_id,
        credits_used=credits_used,
        created_at=datetime.utcnow()
    ))

    # Log user activity in user_activity_logs
    await database.execute(insert(user_activity_logs).values(
        user_id=user_id,
        activity_type="feature_use",
        feature_id=feature_id,
        details=f"Used feature: {feature_name}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        created_at=datetime.utcnow()
    ))
