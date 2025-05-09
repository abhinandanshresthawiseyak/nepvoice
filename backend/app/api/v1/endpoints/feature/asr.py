import shutil
from requests import Session
import requests
from app.database.database import get_db
from app.models.models import User
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from app.dependencies.current_user import get_current_user
from dotenv import load_dotenv
import os

from app.core.enums import LangEnum
from app.api.v1.handlers.feature_asr_handler import send_audio_file

# Load environment variables
load_dotenv()

router = APIRouter()

ASR_FILE_LOCATION = os.getenv("ASR_FILE_LOCATION")
ASR_ENGLISH = os.getenv('ASR_ENGLISH')
ASR_NEPALI = os.getenv('ASR_NEPALI')

@router.post("/", summary="This endpoint accepts audio and get the transcript")
# async def speak_audio(request: Request, lang:str, audio_file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def speak_audio(request: Request, lang:LangEnum, audio_file: UploadFile = File(...), db: Session = Depends(get_db)):
    os.makedirs(ASR_FILE_LOCATION, exist_ok=True)
    file_location = f"{ASR_FILE_LOCATION}/{audio_file.filename}"

    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(audio_file.file, file_object)
    
    try:
        if lang == 'english':
            transcript = send_audio_file(url=ASR_ENGLISH, audio_file_path=file_location)
        elif lang == 'nepali':
            transcript = send_audio_file(url=ASR_NEPALI, audio_file_path=file_location)
        else:
            raise ValueError("Invalid language selected. Only 'english' or 'nepali' are supported.")
        return transcript.strip()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing the audio file.")