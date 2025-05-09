from requests import Session
import requests
from app.database.database import get_db
from app.models.models import User
from fastapi import APIRouter, Depends
from app.dependencies.current_user import get_current_user
from app.models.schemas import CallRequest
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

router = APIRouter()

CALLBOT_URI = os.getenv("CALLBOT_URI")
username=os.getenv("callbot_username")
password=os.getenv("callbot_password")

@router.post("/call", summary="This endpoint allows you to chat with the pdf you ingested")
# async def call(request: CallRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def call(request: CallRequest, db: Session = Depends(get_db)):
    try:
        # Prepare the request data from the incoming request body
        data = {
            'number': request.number,
            'schedule': request.schedule,
            'bank': request.bank
        }
        
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Make the POST request to the external API
        response = requests.post(CALLBOT_URI+'/schedule_call', headers=headers, data=data, auth=HTTPBasicAuth(username, password))

        # Assuming the response is JSON and you want to return this response
        return response.json()  # or adjust based on response format
    except Exception as e:
        print("Exception found:", e)
        raise
    
@router.get("/logs", summary="Gives you the summary of all call logs")
# async def call(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def call_logs(db: Session = Depends(get_db)):
    try:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # Make the POST request to the external API
        response = requests.get(CALLBOT_URI+'/call_logs', headers=headers, auth=HTTPBasicAuth(username, password))

        # Assuming the response is JSON and you want to return this response
        return response.json()  # or adjust based on response format
    except Exception as e:
        print("Exception found:", e)
        raise
    
@router.get("/logs/{caller_id}", summary="This endpoint allows you to get the details of conversation between user and agent")
# async def call(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def call_logs(caller_id, db: Session = Depends(get_db)):
    try:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # Make the POST request to the external API
        response = requests.get(CALLBOT_URI+'/call_logs/'+caller_id, params={"caller_id":caller_id},headers=headers, auth=HTTPBasicAuth(username, password))

        # Assuming the response is JSON and you want to return this response
        return response.json()  # or adjust based on response format
    except Exception as e:
        print("Exception found:", e)
        raise
    
@router.get("/logs/{caller_id}/details", summary="This endpoint allows you to get the details of raw logs stored in the database table")
# async def call(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def call_logs(caller_id, db: Session = Depends(get_db)):
    try:
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        # Make the POST request to the external API
        response = requests.get(CALLBOT_URI+'/call_logs/'+caller_id+'/details', params={"caller_id":caller_id},headers=headers, auth=HTTPBasicAuth(username, password))

        # Assuming the response is JSON and you want to return this response
        return response.json()  # or adjust based on response format
    except Exception as e:
        print("Exception found:", e)
        raise