from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
from sqlalchemy import  text
import numpy as np
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

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

def retrieve_similar_chunks(query: str, db, user_id, top_k: int = 5) -> List[dict]:
    query_embedding = get_query_embedding(query)

    sql = text(f"""
        SELECT a.chunk, a.pdf_id, a.page_number, a.chunk_number, b.total_pages
        FROM vector.pdf_chunks a
        INNER JOIN vector.pdf b on a.pdf_id=b.id
        WHERE a.uploaded_by_user_id=:user_id
        ORDER BY a.embedding <#> (:embedding)::vector
        LIMIT :top_k;
    """)
    result = db.execute(sql, {
        "embedding": query_embedding.tolist(),
        "top_k": top_k,
        "user_id":user_id
    }).fetchall()

    return [{"chunk": row[0], "pdf_id": row[1],"page_number":row[2],"chunk_number":row[3],"total_pages":row[4]} for row in result]

def handle_chat_logic(query, db, user_id):
    all_chunks=retrieve_similar_chunks(query=query, db=db, user_id=user_id)
    print(all_chunks)
    prompt_template = PromptTemplate.from_template("""
        You are a helpful assistant. Use the context below to answer the question. If you don't know the answer, say "I couldn't find relevant answers to your question".

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

    # Use Runnable sequence instead of deprecated LLMChain
    chain = prompt_template | llm

    result = chain.invoke({"context": all_chunks, "question": query})

    # Prepare the response structure
    documents = {}
    for chunk in all_chunks:
        pdf_id = chunk["pdf_id"]
        
        # If pdf_id is not already in the documents, initialize it
        if pdf_id not in documents:
            documents[pdf_id] = {
                "pdf_id": pdf_id,
                "total_pages": chunk["total_pages"],
                "chunk": []
            }
        
        # Append the chunk to the appropriate pdf_id
        documents[pdf_id]["chunk"].append({
            "chunk_number": chunk['chunk_number'],
            "chunk": chunk["chunk"],
            "page_number": chunk["page_number"]
        })

    # Convert the documents dictionary to a list of documents
    document_list = list(documents.values())

    # Return the structured response
    return {
        "response": result.content.strip(),
        "documents": document_list
    }
