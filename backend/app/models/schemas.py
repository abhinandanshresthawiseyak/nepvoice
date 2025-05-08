# Pydantic model to validate the incoming data
from pydantic import BaseModel

class CallRequest(BaseModel):
    number: str
    schedule: int
    bank: str