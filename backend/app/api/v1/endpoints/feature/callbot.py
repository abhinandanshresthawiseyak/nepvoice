# from requests import Session
# import requests
# from app.database.database import get_db
# from app.models.models import User
# from fastapi import APIRouter, Depends
# from app.dependencies.current_user import get_current_user
# from app.models.schemas import CallRequest
# from requests.auth import HTTPBasicAuth
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()

# router = APIRouter()

# CALLBOT_URI = os.getenv("CALLBOT_URI")
# username=os.getenv("callbot_username")
# password=os.getenv("callbot_password")

# @router.post("/call", summary="This endpoint allows you to chat with the pdf you ingested")
# # async def call(request: CallRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# async def call(request: CallRequest, db: Session = Depends(get_db)):
#     try:
#         # Prepare the request data from the incoming request body
#         data = {
#             'number': request.number,
#             'schedule': request.schedule,
#             'bank': request.bank
#         }
        
#         headers = {
#             'accept': 'application/json',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }

#         # Make the POST request to the external API
#         response = requests.post(CALLBOT_URI+'/schedule_call', headers=headers, data=data, auth=HTTPBasicAuth(username, password))

#         # Assuming the response is JSON and you want to return this response
#         return response.json()  # or adjust based on response format
#     except Exception as e:
#         print("Exception found:", e)
#         raise
    
# @router.get("/logs", summary="Gives you the summary of all call logs")
# # async def call(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# async def call_logs(db: Session = Depends(get_db)):
#     try:
#         headers = {
#             'accept': 'application/json',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }
#         # Make the POST request to the external API
#         response = requests.get(CALLBOT_URI+'/call_logs', headers=headers, auth=HTTPBasicAuth(username, password))

#         # Assuming the response is JSON and you want to return this response
#         return response.json()  # or adjust based on response format
#     except Exception as e:
#         print("Exception found:", e)
#         raise
    
# @router.get("/logs/{caller_id}", summary="This endpoint allows you to get the details of conversation between user and agent")
# # async def call(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# async def call_logs(caller_id, db: Session = Depends(get_db)):
#     try:
#         headers = {
#             'accept': 'application/json',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }
#         # Make the POST request to the external API
#         response = requests.get(CALLBOT_URI+'/call_logs/'+caller_id, params={"caller_id":caller_id},headers=headers, auth=HTTPBasicAuth(username, password))

#         # Assuming the response is JSON and you want to return this response
#         return response.json()  # or adjust based on response format
#     except Exception as e:
#         print("Exception found:", e)
#         raise
    
# @router.get("/logs/{caller_id}/details", summary="This endpoint allows you to get the details of raw logs stored in the database table")
# # async def call(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
# async def call_logs(caller_id, db: Session = Depends(get_db)):
#     try:
#         headers = {
#             'accept': 'application/json',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }
#         # Make the POST request to the external API
#         response = requests.get(CALLBOT_URI+'/call_logs/'+caller_id+'/details', params={"caller_id":caller_id},headers=headers, auth=HTTPBasicAuth(username, password))

#         # Assuming the response is JSON and you want to return this response
#         return response.json()  # or adjust based on response format
#     except Exception as e:
#         print("Exception found:", e)
#         raise


# app/routes/callbot.py

from fastapi import APIRouter, Depends
from app.database.mongo import get_mongo_db
from app.models.schemas import CallRequest, CallLog
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import requests
from requests.auth import HTTPBasicAuth
import os

CALLBOT_URI = "http://localhost:8001"  # Or your actual callbot URL
USERNAME = os.getenv("CALLBOT_USER", "admin")
PASSWORD = os.getenv("CALLBOT_PASS", "admin")

router = APIRouter()

@router.post("/call")
async def call(
    request: CallRequest,
    mongo_db: AsyncIOMotorDatabase = Depends(get_mongo_db)
):
    try:
        data = {
            'number': request.number,
            'schedule': request.schedule,
            'bank': request.bank
        }

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(
            f"{CALLBOT_URI}/schedule_call",
            headers=headers,
            data=data,
            auth=HTTPBasicAuth(USERNAME, PASSWORD)
        )

        res_json = response.json()

        # Save success log
        log_entry = CallLog(
            number=request.number,
            schedule=request.schedule,
            bank=request.bank,
            status="success" if response.status_code == 200 else "failed",
            response=res_json
        )
        await mongo_db.call_logs.insert_one(log_entry.dict())

        return res_json

    except Exception as e:
        # Save error log
        await mongo_db.call_logs.insert_one({
            "number": request.number,
            "schedule": request.schedule,
            "bank": request.bank,
            "status": "error",
            "response": str(e),
            "timestamp": datetime.now()
        })
        raise
