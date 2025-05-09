import os
import shutil
from typing import List
from requests import Session
from app.database.database import get_db
from app.api.v1.handlers.feature_chatbot_chat import handle_chat_logic
from app.models.models import PDF, User
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from app.api.v1.handlers.feature_chatbot_ingest_handler import get_pdf_chunks_with_metadata_pymupdf, add_embeddings, save_to_postgres, save_pdf_file
from fastapi.responses import FileResponse
from app.dependencies.current_user import get_current_user

router = APIRouter()

@router.post("/pdf", summary="This endpoint allows you to upload a PDF file, extract its contents, generate embeddings, and store them in the database.")
# async def upload_pdf_to_ingest(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def upload_pdf_to_ingest(files: List[UploadFile], db: Session = Depends(get_db)):
    try:
        # user_id=current_user.id
        user_id='fastapi'
        filenames=[]
        for file in files:
            file_location, pdf_id=save_pdf_file(file, db, user_id=user_id)
            
            if file_location and pdf_id:
                print(f"File saved to {file_location} with pdf_id as {pdf_id}")
                # Process the PDF file
                chunks=get_pdf_chunks_with_metadata_pymupdf(file_location, pdf_id=pdf_id)
                df = add_embeddings(chunks)
                save_to_postgres(df, db, user_id=user_id)
                
                print("Data ingested successfully.")
                filenames.append(file_location)
        return {"files": filenames, "message": "PDFs uploaded successfully, and data ingested."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@router.get("/chat", summary="This endpoint allows you to chat with the pdf you ingested")
# async def chat(query: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def chat(query: str, db: Session = Depends(get_db)):
    try:
        # user_id=current_user.id
        user_id='fastapi'
        
        # Assuming you have a function to handle the chat logic
        response = handle_chat_logic(query=query, db=db, user_id=user_id)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    
@router.get("/pdf", summary="This endpoint allows you to get a PDF file")
# async def get_pdf(pdf_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def get_pdf(pdf_id: int, db: Session = Depends(get_db)):
    try:
        # user_id=current_user.id
        user_id='fastapi'
        
        # Fetch PDF record by ID
        pdf_record = db.query(PDF).filter(PDF.id == pdf_id, PDF.uploaded_by_user_id==user_id).first()

        if not pdf_record:
            raise HTTPException(status_code=404, detail="PDF not found.")

        file_path = pdf_record.filepath

        # Validate file exists on disk
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on server.")

        # Return the file as a response
        return FileResponse(path=file_path, filename=pdf_record.pdf_name, media_type='application/pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")