from fastapi import APIRouter, Query, Request
from app.api.v1.handlers.features_handler import handle_feature_use

router = APIRouter()

# Define endpoints for each feature

@router.get("/features/speech_to_text")
async def use_speech_to_text(user_id: str = Query(...), request: Request = None):
    return await handle_feature_use(user_id, "speech_to_text", request)

@router.get("/features/text_to_speech")
async def use_text_to_speech(user_id: str = Query(...), request: Request = None):
    return await handle_feature_use(user_id, "text_to_speech", request)

@router.get("/features/summarize")
async def use_summarize(user_id: str = Query(...), request: Request = None):
    return await handle_feature_use(user_id, "summarize", request)

@router.get("/features/diarization")
async def use_diarization(user_id: str = Query(...), request: Request = None):
    return await handle_feature_use(user_id, "diarization", request)

@router.get("/features/call_bot")
async def use_call_bot(user_id: str = Query(...), request: Request = None):
    return await handle_feature_use(user_id, "call_bot", request)

@router.get("/features/chatbot")
async def use_chatbot(user_id: str = Query(...), request: Request = None):
    return await handle_feature_use(user_id, "chatbot", request)
