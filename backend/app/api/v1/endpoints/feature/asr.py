from requests import Session
from app.database.database import get_db
from app.models.models import User
from fastapi import APIRouter, Depends
from app.dependencies.current_user import get_current_user
from app.models.schemas import CallRequest
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

router = APIRouter()

@router.post("/ASR", summary="This endpoint allows you to chat with the pdf you ingested")
# async def call(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def call_asr(db: Session = Depends(get_db)):
    pass