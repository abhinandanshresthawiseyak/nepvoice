import shutil, requests, os
from requests import Session
from app.database.database import get_db
from app.models.models import User, ASRHistory
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from app.dependencies.current_user import get_current_user
from dotenv import load_dotenv
from app.core.enums import LangEnum
from app.api.v2.handlers.feature_asr_handler import send_audio
from app.utils.minio_utils import upload_audio_to_minio, read_object_from_minio
from app.utils.kafkaclient import KafkaClient
import logging, uuid, random, json
from datetime import datetime
# Load environment variables
load_dotenv()

router = APIRouter()

# ASR_FILE_LOCATION = os.getenv("ASR_FILE_LOCATION")
ASR_ENGLISH = os.getenv('ASR_ENGLISH')
ASR_NEPALI = os.getenv('ASR_NEPALI')
MINIO_BUCKET = os.getenv('MINIO_BUCKET')
ASR_OBJECT_PREFIX = os.getenv('ASR_OBJECT_PREFIX')
KAFKA_SERVER = os.getenv('KAFKA_SERVER')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Initialize Kafka client
    kafkaClient = KafkaClient(bootstrap_servers=KAFKA_SERVER)
    kafkaClient.initialize_producer()
    kafkaClient.initialize_admin_client()
    kafkaClient.create_topic(topic_name='asr_request_queue_topic', num_partitions=3, replication_factor=1, config={"max.message.bytes": 10485760})
    kafkaClient.create_topic(topic_name='asr_response_queue_topic', num_partitions=3, replication_factor=1, config={"max.message.bytes": 10485760})
except Exception as e:
    logger.info(f"Error initializing Kafka client: {e}")
    raise HTTPException(status_code=500, detail=str(e))

@router.post("", summary="This endpoint accepts audio and get the transcript")
# async def speak_audio(request: Request, lang:str, audio_file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def speak_audio(request: Request, lang:LangEnum, audio_file: UploadFile = File(...), db: Session = Depends(get_db)):
    ip_address = request.client.host if request else "unknown"
    user_agent = request.headers.get("user-agent") if request else "unknown"
    session_id = request.cookies.get("session")  # or None
    
    # Generate UUID
    base_id = str(uuid.uuid4())
    extra_random = str(random.randint(10**7, 10**8 - 1))  # ensures 8 digits
    request_id = f"{base_id}-{extra_random}"
    user_id='admin_manual_1'
    
    try:
        # Read file content into bytes
        audio_bytes = await audio_file.read()
        bucket_name, object_name= upload_audio_to_minio(audio_bytes=audio_bytes, bucket_name=MINIO_BUCKET, object_name=f"{ASR_OBJECT_PREFIX}/{audio_file.filename}")
        kafkaClient.producer.produce('asr_request_queue_topic', key=request_id, value=json.dumps({"request_id": request_id, "ip_address":ip_address, "user_agent":user_agent, "session_id":session_id, "user_id":user_id, "type": "asr_queue", "lang":lang, "bucket_name":bucket_name, "object_name":object_name, "timestamp": str(datetime.now())}), callback=kafkaClient.delivery_report)
        
        return {"message": "Text generation request has been sent to the queue.", "request_id": request_id}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")
    
    
@router.get("/{request_id}", summary="Get transcript for a given request ID")
# async def get_transcript(request_id: str, current_user: User = Depends(get_current_user)):
async def get_transcript(request_id: str):
    try:
        object_name = f"{ASR_OBJECT_PREFIX}/{request_id}.txt"
        
        # Read the object from MinIO
        text_content = read_object_from_minio(bucket_name=MINIO_BUCKET, object_name=object_name)
        
        if not text_content:
            raise HTTPException(status_code=404, detail="Transcript not found or is empty.")

        return {"request_id": request_id, "transcript": text_content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch transcript: {e}")