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
from app.models.models import ASRHistory


from app.api.v1.handlers.features_handler import handle_feature_use

from app.dependencies.api_key_user import get_user_from_api_key


# Load environment variables
load_dotenv()

router = APIRouter()

ASR_FILE_LOCATION = os.getenv("ASR_FILE_LOCATION")
ASR_ENGLISH = os.getenv('ASR_ENGLISH')
ASR_NEPALI = os.getenv('ASR_NEPALI')

# @router.post("/", summary="This endpoint accepts audio and get the transcript")
# # async def speak_audio(request: Request, lang:str, audio_file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# async def speak_audio(request: Request, lang:LangEnum, audio_file: UploadFile = File(...), db: Session = Depends(get_db)):
#     os.makedirs(ASR_FILE_LOCATION, exist_ok=True)
#     file_location = f"{ASR_FILE_LOCATION}/{audio_file.filename}"

#     with open(file_location, "wb+") as file_object:
#         shutil.copyfileobj(audio_file.file, file_object)
    
#     try:
#         if lang == 'english':
#             transcript = send_audio_file(url=ASR_ENGLISH, audio_file_path=file_location)
            
#         elif lang == 'nepali':
#             transcript = send_audio_file(url=ASR_NEPALI, audio_file_path=file_location)
#         else:
#             raise ValueError("Invalid language selected. Only 'english' or 'nepali' are supported.")
        
#         return transcript.strip()
#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")





# @router.post("/", summary="This endpoint accepts audio and get the transcript")
# async def speak_audio(
#     request: Request,
#     lang: LangEnum,
#     audio_file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     os.makedirs(ASR_FILE_LOCATION, exist_ok=True)
#     file_location = f"{ASR_FILE_LOCATION}/{audio_file.filename}"

#     with open(file_location, "wb+") as file_object:
#         shutil.copyfileobj(audio_file.file, file_object)

#     try:
#         if lang == 'english':
#             transcript = send_audio_file(url=ASR_ENGLISH, audio_file_path=file_location)
#         elif lang == 'nepali':
#             transcript = send_audio_file(url=ASR_NEPALI, audio_file_path=file_location)
#         else:
#             raise ValueError("Invalid language selected. Only 'english' or 'nepali' are supported.")

#         from app.models.models import ASRHistory  # Import here to avoid circular import issues
#         asr_record = ASRHistory(
#             user_id=current_user.id if current_user else None,
#             language=lang,
#             transcript=transcript.strip(),
#             audio_path=file_location
#         )
#         db.add(asr_record)
#         db.commit()
#         db.refresh(asr_record)

#         return transcript.strip()

#     except ValueError as ve:
#         raise HTTPException(status_code=400, detail=str(ve))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")


@router.post("/", summary="This endpoint accepts audio and get the transcript")
async def speak_audio(
    request: Request,
    lang: LangEnum,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --- 1. Automatic credit deduction ---
    ip_address = request.client.host if request else "unknown"
    user_agent = request.headers.get("user-agent") if request else "unknown"
    session_id = request.cookies.get("session")  # or None

    # Call credit deduction
    result, error = handle_feature_use(
        user_id=current_user.id,
        feature_name="speech_to_text",  # your feature name in DB
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )
    if error:
        if error == "Feature not found.":
            raise HTTPException(status_code=404, detail=error)
        elif error == "User wallet not found.":
            raise HTTPException(status_code=404, detail=error)
        elif error == "Insufficient credits.":
            raise HTTPException(status_code=402, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)

    # --- 2. Proceed with the rest of your ASR logic ---
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

        asr_record = ASRHistory(
            user_id=current_user.id if current_user else None,
            language=lang,
            transcript=transcript.strip(),
            audio_path=file_location
        )
        db.add(asr_record)
        db.commit()
        db.refresh(asr_record)

        return transcript.strip()

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")






@router.get("/history", summary="Get all ASR history of the current user")
async def get_asr_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(ASRHistory).filter(ASRHistory.user_id == current_user.id).all()
    return [
        {
            "id": record.id,
            "language": record.language,
            "transcript": record.transcript,
            "audio_path": record.audio_path,
            "timestamp": record.created_at,
        }
        for record in history
    ]


@router.post("/api_asr", summary="This endpoint accepts audio and gets the transcript")
async def speak_audio(
    request: Request,
    lang: LangEnum,
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # OAuth fallback
    api_user: User = Depends(get_user_from_api_key)  # API Key fallback
):
    user = api_user or current_user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    # --- Credit deduction ---
    ip_address = request.client.host if request else "unknown"
    user_agent = request.headers.get("user-agent") if request else "unknown"
    session_id = request.cookies.get("session")

    result, error = handle_feature_use(
        user_id=user.id,
        feature_name="speech_to_text",
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    # --- File saving + transcription logic ---
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
            raise ValueError("Invalid language selected.")

        asr_record = ASRHistory(
            user_id=current_user.id if current_user else None,
            language=lang,
            transcript=transcript.strip(),
            audio_path=file_location
        )
        db.add(asr_record)
        db.commit()
        db.refresh(asr_record)

        return transcript.strip()

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio file: {e}")


