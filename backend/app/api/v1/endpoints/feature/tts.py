from fastapi.responses import FileResponse
from requests import Session
from app.database.database import get_db
from app.models.models import User
from fastapi import APIRouter, Depends, File, HTTPException, Request
from app.dependencies.current_user import get_current_user
from dotenv import load_dotenv
from app.models.models import TTSHistory


from app.core.enums import LangEnum
from app.api.v1.handlers.feature_tts_handler import generate_tts_audio


# Load environment variables
load_dotenv()

router = APIRouter()

# @router.get("/", summary="This endpoint accepts text and returns audio file")
# # async def speak_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# async def get_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db)):
#     try:
#         audio_file_path=generate_tts_audio(text=text,language=lang)
#         return FileResponse(path=audio_file_path, media_type="audio/wav")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")


@router.get("", summary="This endpoint accepts text and returns audio file")
async def get_audio(
    request: Request,
    text: str,
    lang: LangEnum,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # enable user tracking
):
    try:
        audio_file_path = generate_tts_audio(text=text, language=lang)

        # Save record in DB
        tts_record = TTSHistory(
            user_id=current_user.id,
            text=text,
            language=lang.value,
            audio_file_path=audio_file_path
        )
        db.add(tts_record)
        db.commit()
        db.refresh(tts_record)

        return FileResponse(path=audio_file_path, media_type="audio/wav")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")


@router.get("/history", summary="Get TTS conversion history")
async def get_tts_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    history = db.query(TTSHistory).filter_by(user_id=current_user.id).order_by(TTSHistory.timestamp.desc()).all()
    return history
