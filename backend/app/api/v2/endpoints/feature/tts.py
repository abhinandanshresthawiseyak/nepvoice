from fastapi.responses import FileResponse
from requests import Session
from app.database.database import get_db
from app.models.models import User
from fastapi import APIRouter, Depends, File, HTTPException, Request, WebSocket
from app.dependencies.current_user import get_current_user
from dotenv import load_dotenv
import uuid, json
from app.core.enums import LangEnum
from app.api.v2.handlers.feature_tts_handler import generate_tts_audio
from app.utils.kafkaclient import KafkaClient
from datetime import datetime

# Load environment variables
load_dotenv()

router = APIRouter()

try:
    # Initialize Kafka client
    kafkaClient = KafkaClient(bootstrap_servers='192.168.88.40:19092, 192.168.88.40:19093')
    kafkaClient.initialize_producer()
    kafkaClient.initialize_admin_client()
    kafkaClient.create_topic(topic_name='tts_request_queue_topic', num_partitions=3, replication_factor=1, config={"max.message.bytes": 10485760})
    kafkaClient.create_topic(topic_name='tts_response_queue_topic', num_partitions=3, replication_factor=1, config={"max.message.bytes": 10485760})
except Exception as e:
    print(f"Error initializing Kafka client: {e}")
    raise HTTPException(status_code=500, detail=str(e))

@router.get("", summary="This endpoint accepts text and returns audio file")
# async def speak_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def get_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db)):
    request_id=str(uuid.uuid4())
    try:
        kafkaClient.producer.produce('tts_request_queue_topic', key=request_id, value=json.dumps({"request_id": request_id, "type": "tts_queue","lang":lang,"text":text, "timestamp": str(datetime.now())}), callback=kafkaClient.delivery_report)
        kafkaClient.producer.flush()
        print(f"Message produced successfully to tts-queue-topic.")
        return {"message": "Audio generation request has been sent to the queue.", "request_id": request_id}
    except Exception as e:
        print(f"Producer exception: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to produce message to Kafka topic: tts-queue-topic.")
    
    # audio_file_path=generate_tts_audio(text=text,language=lang)
    # return FileResponse(path=audio_file_path, media_type="audio/wav")
  