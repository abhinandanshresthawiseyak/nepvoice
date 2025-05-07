from fastapi import HTTPException
import shutil
from typing import List, Dict, Any
from app.models.models import PDFChunk
import fitz
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pymupdf  # import package PyMuPDF
import pandas as pd
from app.database.database import engine
from dotenv import load_dotenv
import os

load_dotenv()  # This loads variables from .env into environment

api_key = os.getenv("gemini_api_key")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)

def save_pdf_file(file):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        file_location = os.path.join("/files", file.filename)

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return file_location
    except Exception as e:
        raise 
    
def get_pdf_chunks_with_metadata_pymupdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extracts all text chunks from PDFs using PyMuPDF, along with their PDF name, page number, chunk number, and rectangles (coordinates).
    """
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    pdf_name = pdf_path.split('/')[-1]
    doc = fitz.open(pdf_path)
    
    for page_number, page in enumerate(doc, start=1):
        page_text = page.get_text()
        if not page_text:
            continue
        chunks = text_splitter.split_text(page_text)
        for chunk_number, chunk in enumerate(chunks, start=1):
            if chunk:
                # search_for may not find the chunk if it spans lines or is split oddly
                rects = page.search_for(chunk)
                # print(rects)
                all_chunks.append({
                    "chunk": chunk,
                    # "rects": rects,
                    "pdf_name": pdf_name,
                    "page_number": page_number,
                    "chunk_number": chunk_number
                })
    return all_chunks

def add_embeddings(chunks):
    df = pd.DataFrame(chunks)
    # Generate embeddings for each chunk and append as a new column
    chunk_texts = df['chunk'].tolist()
    embeddings_list = embeddings.embed_documents(chunk_texts)
    df['embedding'] = embeddings_list
    return df

def save_to_postgres(df, db):
    try:
        for _, row in df.iterrows():
            chunk = PDFChunk(
                chunk=row['chunk'],
                pdf_name=row['pdf_name'],
                page_number=int(row['page_number']),
                chunk_number=int(row['chunk_number']),
                embedding=row['embedding']  # Should be a list or NumPy array of floats
            )
            db.add(chunk)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

# # Convert to DataFrame and display
# chunks = get_pdf_chunks_with_metadata_pymupdf('/home/mirage/wiseyak/abhi/chatbot_indexing/test.pdf')
# df = add_embeddings(chunks)

