import shutil, requests, os
from requests import Session
from app.database.database import get_db
from app.models.models import User
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from app.dependencies.current_user import get_current_user
from dotenv import load_dotenv
from app.core.enums import LangEnum
from app.api.v2.handlers.feature_asr_handler import send_audio
from app.utils.minio_utils import upload_audio_to_minio
# Load environment variables
load_dotenv()

router = APIRouter()

# ASR_FILE_LOCATION = os.getenv("ASR_FILE_LOCATION")
ASR_ENGLISH = os.getenv('ASR_ENGLISH')
ASR_NEPALI = os.getenv('ASR_NEPALI')

@router.post("", summary="This endpoint accepts audio and get the transcript")
# async def speak_audio(request: Request, lang:str, audio_file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def speak_audio(request: Request, lang:LangEnum, audio_file: UploadFile = File(...), db: Session = Depends(get_db)):

    try:
        # Read file content into bytes
        audio_bytes = await audio_file.read()
        audio_name= upload_audio_to_minio(audio_bytes=audio_bytes, bucket_name='asr-audios', object_name=audio_file.filename)
        print(audio_name)
        if lang == 'english':
            transcript = send_audio(url=ASR_ENGLISH, audio_name=audio_name)
        elif lang == 'nepali':
            transcript = send_audio(url=ASR_NEPALI, audio_name=audio_name)
        else:
            raise ValueError("Invalid language selected. Only 'english' or 'nepali' are supported.")
        return transcript.strip()
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")