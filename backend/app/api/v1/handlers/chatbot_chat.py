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
from sqlalchemy import  text
import numpy as np
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain

# Load environment variables
load_dotenv()
api_key = os.getenv("gemini_api_key")
os.environ["GOOGLE_API_KEY"] = api_key

# Initialize the embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=api_key
)

def get_query_embedding(query: str):
    """
    Generate an embedding for a single query string using Google Generative AI embeddings.
    Returns a numpy array to support .tolist().
    """
    embedding = embeddings.embed_query(query)
    return np.array(embedding, dtype=np.float32)  # ensure it's a NumPy array

def retrieve_similar_chunks(query: str, db, top_k: int = 5) -> List[dict]:
    query_embedding = get_query_embedding(query)

    sql = text("""
        SELECT chunk, pdf_name, page_number, chunk_number
        FROM vector.pdf_chunks
        ORDER BY embedding <#> (:embedding)::vector
        LIMIT :top_k;
    """)
    result = db.execute(sql, {
        "embedding": query_embedding.tolist(),
        "top_k": top_k
    }).fetchall()

    return [{"chunk": row[0], "pdf_name": row[1],"page_number":row[2],"chunk_number":row[3]} for row in result]

def handle_chat_logic(query, db):
    all_chunks=retrieve_similar_chunks(query=query, db=db)
    print(all_chunks)
    prompt_template = PromptTemplate.from_template("""
        You are a helpful assistant. Use the context below to answer the question.

        Context:
        {context}

        Question:
        {question}

        Answer:
    """)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2
    )

    chain = LLMChain(llm=llm, prompt=prompt_template)
    result = chain.run({"context": all_chunks, "question": query})
    return {"response": result, "chunks": all_chunks}