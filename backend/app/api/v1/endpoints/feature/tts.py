import shutil
from fastapi.responses import FileResponse
from requests import Session
import requests
from app.database.database import get_db
from app.models.models import User
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from app.dependencies.current_user import get_current_user
from dotenv import load_dotenv
import os
import uuid
from app.core.enums import LangEnum
from app.api.v1.handlers.feature_asr_handler import send_audio_file

# Load environment variables
load_dotenv()

router = APIRouter()

TTS_URI=os.getenv('TTS')
TTS_FILE_LOCATION=os.getenv('TTS_FILE_LOCATION')
TTS_API_KEY=os.getenv('TTS_API_KEY')

def generate_tts_audio(text: str, language: str):
    """
    Helper function to generate TTS audio for the given text and language.
    """
    query_params = {
        "audio_flag": "true",
        "is_container": "false"
    }
    
    payload = {"text": text, 
               "language": language}

    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        "x-api-key": TTS_API_KEY
    }

    try:
        response = requests.post(TTS_URI, params=query_params, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        audio_filename = f"{uuid.uuid4()}.wav"
        audio_file_path = os.path.join(TTS_FILE_LOCATION, audio_filename)
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(response.content)
        return audio_file_path
    except requests.exceptions.Timeout:
        audio_path_tts = "connection timeout"
        return audio_path_tts
    except requests.exceptions.RequestException as e:
        print(e)
        return None

@router.get("/", summary="This endpoint accepts text and returns audio file")
# async def speak_audio(request: Request, lang:str, audio_file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def get_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db)):
    audio_file_path=generate_tts_audio(text=text,language=lang)
    return FileResponse(path=audio_file_path, media_type="audio/wav")