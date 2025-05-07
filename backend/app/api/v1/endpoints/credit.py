from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.v1.handlers import credit_handler

router = APIRouter()

class CreditPurchaseRequest(BaseModel):
    user_id: str
    credit_amount: int

@router.post("/simulate_purchase")
def simulate_purchase(data: CreditPurchaseRequest):
    new_balance, error = credit_handler.simulate_purchase(data.user_id, data.credit_amount)
    if error:
        raise HTTPException(status_code=404, detail=error)

    return {
        "message": f"{data.credit_amount} credits added to user {data.user_id}.",
        "new_balance": new_balance
    }
