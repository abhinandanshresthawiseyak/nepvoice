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
from app.database.mongo import mongo_db
from datetime import datetime

# Load environment variables
load_dotenv()

router = APIRouter()

CALLBOT_URI = os.getenv("CALLBOT_URI")
username=os.getenv("callbot_username")
password=os.getenv("callbot_password")

# @router.post("/call", summary="This endpoint allows you to call the customer")
# async def call(request: CallRequest, db: Session = Depends(get_db)):
#     try:
#         data = {
#             'number': request.number,
#             'schedule': request.schedule,
#             'bank': request.bank
#         }

#         headers = {
#             'accept': 'application/json',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }

#         response = requests.post(
#             CALLBOT_URI+'/schedule_call',
#             headers=headers,
#             data=data,
#             auth=HTTPBasicAuth(username, password)
#         )

#         result = response.json()

#         # Save call request and response in MongoDB
#         call_log = {
#             "number": request.number,
#             "schedule": request.schedule,
#             "bank": request.bank,
#             "timestamp": datetime.utcnow(),
#             "response": result
#         }

#         await mongo_db.call_logs.insert_one(call_log)

#         return result

#     except Exception as e:
#         print("Exception found:", e)
#         raise
from app.models.models import UserDetails
from app.database.mongo import mongo_db
from datetime import datetime, timezone
import uuid
import logging

# @router.post("/call", summary="This endpoint allows you to call the customer")
# async def call(request: CallRequest, db: Session = Depends(get_db)):
#     try:
#         # STEP 1: External API call
#         data = {
#             'number': request.number,
#             'schedule': request.schedule,
#             'bank': request.bank
#         }

#         headers = {
#             'accept': 'application/json',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }

#         response = requests.post(
#             CALLBOT_URI + '/schedule_call',
#             headers=headers,
#             data=data,
#             auth=HTTPBasicAuth(username, password)
#         )

#         try:
#             result = response.json()
#         except ValueError:
#             result = {
#                 "error": "Invalid JSON response",
#                 "status_code": response.status_code,
#                 "raw": response.text
#             }

#         # STEP 2: Unique caller_id
#         caller_id = str(uuid.uuid4())

#         # STEP 3: Save to PostgreSQL
#         new_user = UserDetails(
#             caller_id=caller_id,
#             name="Saugat",  # Or pull from current_user if available
#             phone_number=request.number,
#             tts_folder_location="/files/atm_capture_session123/",
#             status="initiated",
#             assigned_container="container-1",
#             scheduled_for_utc=datetime.now(timezone.utc),
#             modified_on_utc=datetime.now(timezone.utc)
#         )
#         db.add(new_user)
#         db.commit()

#         # STEP 4: Save call_type JSON to MongoDB
#         # call_type_json = {
#         #     "type": "atm_capture",
#         #     "question_audio_for_tts": { ... },  # paste your full JSON here
#         #     "llm_states": { ... },
#         #     "tts_next_states": { ... }
#         # }
#         call_type_json = {
#     "type": "atm_capture",
#     "question_audio_for_tts": {
#         "1": {
#             "yes": "नमस्ते! म ग्लोबल बैंकबाट प्रतिवा बोल्दैछु! के तपाईं {name} जी बोल्दै हुनुहुन्छ!"
#         }
#     },
#     "llm_states": {
#         "1": {
#             "positive": ["हजुर बोल्दै छु"],
#             "negative": ["हैन"]
#         }
#     },
#     "tts_next_states": {
#         "1": {
#             "yes": {"next_state": 2, "audio_file": "atm_capture2yes.wav"},
#             "no": {"next_state": "out_state", "audio_file": "atm_capture2no.wav"},
#             "repeat": {"next_state": 1, "audio_file": "atm_capture1.wav"}
#         }
#     }
# }


#         await mongo_db.call_types.insert_one({
#             "caller_id": caller_id,
#             "call_type": call_type_json,
#             "created_at": datetime.now()
#         })

#         logging.info(f"Saved user {caller_id} in both Postgres and MongoDB.")
#         return {"status": "success", "caller_id": caller_id, "callbot_response": result}

#     except Exception as e:
#         logging.error(f"Call failed: {e}")
#         raise

from fastapi import APIRouter, Depends
from app.models.schemas import CallRequest
from app.models.models import UserDetails
from app.database.database import get_db
from app.database.mongo import mongo_db
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from uuid import uuid4
import requests
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

CALLBOT_URI = os.getenv("CALLBOT_URI")
username = os.getenv("callbot_username")
password = os.getenv("callbot_password")


@router.post("/call", summary="Schedule a call and save call type to MongoDB")
async def call(request: CallRequest, db: Session = Depends(get_db)):
    try:
        # Prepare data and headers
        data = {
            'number': request.number,
            'schedule': request.schedule,
            'bank': request.bank
        }

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Make POST request to external callbot API
        response = requests.post(
            CALLBOT_URI + '/schedule_call',
            headers=headers,
            data=data,
            auth=HTTPBasicAuth(username, password)
        )

        try:
            result = response.json()
        except ValueError:
            result = {
                "error": "Invalid JSON response",
                "status_code": response.status_code,
                "raw": response.text
            }

        # Generate unique caller_id
        caller_id = str(uuid4())

        # Save user call metadata to PostgreSQL
        new_user = UserDetails(
            caller_id=caller_id,
            name=result.get("name", "Unknown"),  # fallback if name missing
            phone_number=request.number,
            status=result.get("status", "unknown"),
            tts_folder_location=result.get("tts_folder_location", ""),
            assigned_container=result.get("assigned_container", ""),
            scheduled_for_utc=datetime.fromisoformat(result.get("scheduled_for_utc")) if result.get("scheduled_for_utc") else datetime.now(timezone.utc),
            modified_on_utc=datetime.fromisoformat(result.get("modified_on_utc")) if result.get("modified_on_utc") else datetime.now(timezone.utc)
        )
        db.add(new_user)
        db.commit()

        # Parse and save call_type to MongoDB
        call_type_raw = result.get("call_type")
        call_type_dict = None
        if call_type_raw:
            try:
                call_type_dict = json.loads(call_type_raw)
            except Exception as e:
                logging.warning(f"[call_type] Invalid JSON in response: {e}")

        if call_type_dict:
            await mongo_db.call_types.insert_one({
                "caller_id": caller_id,
                "call_type": call_type_dict,
                "timestamp": datetime.utcnow()
            })
            logging.info(f"[Mongo] Inserted call_type for {caller_id}")
        else:
            logging.warning("No valid call_type found. Skipping Mongo insert.")

        return {
            "status": "success",
            "caller_id": caller_id,
            "callbot_response": result
        }

    except Exception as e:
        logging.error(f"Exception in /call: {e}")
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

        return response.json() 
    except Exception as e:
        print("Exception found:", e)
        raise

@router.get("/mongo_call_type/{caller_id}")
async def get_call_type(caller_id: str):
    doc = await mongo_db.call_types.find_one({"caller_id": caller_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc or {"error": "Not found"}
