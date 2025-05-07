import os
import shutil
from requests import Session
from app.database.database import get_db
from app.api.v1.handlers.chatbot_chat import handle_chat_logic
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from app.api.v1.handlers.chatbot_ingest_handler import get_pdf_chunks_with_metadata_pymupdf, add_embeddings, save_to_postgres

router = APIRouter()

@router.post("/upload_pdf_to_ingest")
async def upload_pdf_to_ingest(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        file_location = os.path.join("/files", file.filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"File saved to {file_location}")
        
        # Process the PDF file
        chunks=get_pdf_chunks_with_metadata_pymupdf(file_location)
        df = add_embeddings(chunks)
        save_to_postgres(df, db)
        
        print("Data ingested successfully.")
        return {"filename": file.filename, "message": "PDF uploaded successfully, and data ingested."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.get("/chat")
async def chat(query: str, db: Session = Depends(get_db)):
    try:
        # Assuming you have a function to handle the chat logic
        response = handle_chat_logic(query, db)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")