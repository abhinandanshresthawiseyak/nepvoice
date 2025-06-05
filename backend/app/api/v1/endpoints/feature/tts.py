# from fastapi.responses import FileResponse
# from requests import Session
# from app.database.database import get_db
# from app.models.models import User
# from fastapi import APIRouter, Depends, File, HTTPException, Request
# from app.dependencies.current_user import get_current_user
# from dotenv import load_dotenv
# from app.models.models import TTSHistory


# from app.core.enums import LangEnum
# from app.api.v1.handlers.feature_tts_handler import generate_tts_audio


# # Load environment variables
# load_dotenv()

# router = APIRouter()

# # @router.get("/", summary="This endpoint accepts text and returns audio file")
# # # async def speak_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# # async def get_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db)):
# #     try:
# #         audio_file_path=generate_tts_audio(text=text,language=lang)
# #         return FileResponse(path=audio_file_path, media_type="audio/wav")
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")


# @router.get("", summary="This endpoint accepts text and returns audio file")
# async def get_audio(
#     request: Request,
#     text: str,
#     lang: LangEnum,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)  # enable user tracking
# ):
#     try:
#         audio_file_path = generate_tts_audio(text=text, language=lang)

#         # Save record in DB
#         tts_record = TTSHistory(
#             user_id=current_user.id,
#             text=text,
#             language=lang.value,
#             audio_file_path=audio_file_path
#         )
#         db.add(tts_record)
#         db.commit()
#         db.refresh(tts_record)

#         return FileResponse(path=audio_file_path, media_type="audio/wav")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")


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
from app.api.v1.handlers.features_handler import handle_feature_use

from app.dependencies.api_key_user import get_user_from_api_key 
# Load environment variables
load_dotenv()

router = APIRouter()

@router.get("", summary="This endpoint accepts text and returns audio file")
async def get_audio(
    request: Request,
    text: str,
    lang: LangEnum,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # enable user tracking
):
    # 1. Deduct credits automatically for 'tts' feature
    ip_address = request.client.host if request else "unknown"
    user_agent = request.headers.get("user-agent") if request else "unknown"
    session_id = request.cookies.get("session")

    result, error = handle_feature_use(
        user_id=current_user.id,
        feature_name="text_to_speech",
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

    # 2. Proceed with your original TTS logic
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



@router.get("/api_tts", summary="TTS via API key or OAuth")
async def get_audio_via_api_key(
    request: Request,
    text: str,
    lang: LangEnum,
    db: Session = Depends(get_db),
    api_user: User = Depends(get_user_from_api_key),
    current_user: User = Depends(get_current_user)
):
    # Fallback logic: use API key if present, else OAuth
    user = api_user or current_user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # --- Deduct credits ---
    ip_address = request.client.host if request else "unknown"
    user_agent = request.headers.get("user-agent") if request else "unknown"
    session_id = request.cookies.get("session")

    result, error = handle_feature_use(
        user_id=user.id,
        feature_name="text_to_speech",
        ip_address=ip_address,
        user_agent=user_agent,
        session_id=session_id
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    # --- Generate audio ---
    try:
        audio_file_path = generate_tts_audio(text=text, language=lang)

        # Save record in DB
        tts_record = TTSHistory(
            user_id=user.id,
            text=text,
            language=lang.value,
            audio_file_path=audio_file_path
        )
        db.add(tts_record)
        db.commit()
        db.refresh(tts_record)

        # return FileResponse(path=audio_file_path, media_type="audio/wav")
        return FileResponse(
    path=audio_file_path,
    media_type="audio/wav",
    filename="tts_output.wav",
    headers={"Content-Disposition": "inline; filename=tts_output.wav"}
)


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")
