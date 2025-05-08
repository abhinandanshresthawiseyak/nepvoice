import os
import shutil
from requests import Session
from app.database.database import get_db
from app.api.v1.handlers.feature_chatbot_chat import handle_chat_logic
from app.models.models import PDF, User
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from app.api.v1.handlers.feature_chatbot_pdf_ingestion import get_pdf_chunks_with_metadata_pymupdf, add_embeddings, save_to_postgres, save_pdf_file
from fastapi.responses import FileResponse
from app.dependencies.current_user import get_current_user

router = APIRouter()

@router.get("/call", description="This endpoint allows you to chat with the pdf you ingested")
async def call(query: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pass