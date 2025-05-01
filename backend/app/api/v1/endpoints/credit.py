from fastapi import APIRouter, Query
from app.api.v1.handlers.credit_handler import simulate_credit_purchase

router = APIRouter()

@router.post("/credits/simulate")
async def simulate_credits(user_id: str = Query(...), credit_amount: int = Query(...)):
    """
    Simulate a credit purchase by adding credits to a user's wallet.
    """
    return await simulate_credit_purchase(user_id, credit_amount)
