from fastapi.responses import FileResponse, StreamingResponse
from requests import Session
from app.database.database import get_db
from app.models.models import User
from fastapi import APIRouter, Depends, File, HTTPException, Request, WebSocket
from app.dependencies.current_user import get_current_user
from dotenv import load_dotenv
import uuid, json, re
from app.core.enums import LangEnum
from app.api.v2.handlers.feature_tts_handler import generate_tts_audio, TTSPreprocessor, audio_chunk_generator
from app.utils.kafkaclient import KafkaClient
from app.utils.minio_utils import read_object_from_minio, upload_audio_to_minio
from datetime import datetime
from io import BytesIO
import random, asyncio, os, logging
from pydub import AudioSegment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    kafkaClient.create_topic(topic_name='tts_streaming_request_queue_topic', num_partitions=3, replication_factor=1, config={"max.message.bytes": 10485760})
    kafkaClient.create_topic(topic_name='tts_streaming_response_queue_topic', num_partitions=1, replication_factor=1, config={"max.message.bytes": 10485760})
except Exception as e:
    logger.info(f"Error initializing Kafka client: {e}")
    raise HTTPException(status_code=500, detail=str(e))

@router.get("/streaming", summary="This endpoint accepts text and returns audio file")
# async def speak_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def get_audio_stream(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db)):
    # Generate UUID
    base_id = str(uuid.uuid4())
    extra_random = str(random.randint(10**7, 10**8 - 1))  # ensures 8 digits
    request_id = f"{base_id}-{extra_random}"
    segments=TTSPreprocessor().preprocess_and_split_text(text=text, language=lang)
    try:
        
        for segment in segments:
            kafkaClient.producer.produce('tts_streaming_request_queue_topic', key=request_id, value=json.dumps({"request_id": request_id, "type": "tts_queue","lang":lang,"text":segment, "timestamp": str(datetime.now())}), callback=kafkaClient.delivery_report)
        
        kafkaClient.producer.produce('tts_streaming_request_queue_topic', key=request_id, value=json.dumps({"request_id": request_id, "type": "tts_queue","lang":lang,"text":'EndOfStream', "timestamp": str(datetime.now())}), callback=kafkaClient.delivery_report)
        kafkaClient.producer.flush()
        
        logging.info(f"Message produced successfully to tts-queue-topic.")
        return {"message": "Audio generation request has been sent to the queue.", "request_id": request_id}
    except Exception as e:
        logging.info("Producer exception: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to produce message to Kafka topic: tts-queue-topic.")
    
@router.get("/streaming/{request_id}", summary="This endpoint accepts text and returns audio file")
# async def speak_audio(request: Request, request_id:str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def get_audio_stream_for_request(request: Request, request_id:str, db: Session = Depends(get_db)):
    try:
        kafkaClient.initialize_consumer(group_id=request_id, auto_offset_reset='earliest')
        kafkaClient.check_kafka_connection()
        # kafkaClient.consumer.subscribe([request_id])
        kafkaClient.consumer.subscribe(['tts_streaming_response_queue_topic'])
        return StreamingResponse(audio_chunk_generator(request_id, kafkaClient), media_type="audio/mpeg")
        # kafkaClient.consumer.close()
    except Exception as e:
        logging.info("Error retrieving audio for request_id %s:%s",request_id, str(e))
        raise HTTPException(status_code=404, detail=f"Audio not found for request_id: {request_id}")


@router.get("", summary="This endpoint accepts text and returns audio file")
# async def speak_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def get_audio(request: Request, text:str, lang:LangEnum, db: Session = Depends(get_db)):
    # Generate UUID
    base_id = str(uuid.uuid4())
    extra_random = str(random.randint(10**7, 10**8 - 1))  # ensures 8 digits
    request_id = f"{base_id}-{extra_random}"
    # segments=TTSPreprocessor().preprocess_and_split_text(text=text, language=lang)
    try:
        # for segment in segments:
            # kafkaClient.producer.produce('tts_request_queue_topic', key=request_id, value=json.dumps({"request_id": request_id, "type": "tts_queue","lang":lang,"text":segment, "timestamp": str(datetime.now())}), callback=kafkaClient.delivery_report)
        kafkaClient.producer.produce('tts_request_queue_topic', key=request_id, value=json.dumps({"request_id": request_id, "type": "tts_queue","lang":lang,"text":text, "timestamp": str(datetime.now())}), callback=kafkaClient.delivery_report)
        kafkaClient.producer.flush()
        logging.info(f"Message produced successfully to tts-queue-topic.")
        return {"message": "Audio generation request has been sent to the queue.", "request_id": request_id}
    except Exception as e:
        logging.info(f"Producer exception: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to produce message to Kafka topic: tts-queue-topic.")
    
    # audio_file_path=generate_tts_audio(text=text,language=lang)
    # return FileResponse(path=audio_file_path, media_type="audio/wav")

@router.get("/{request_id}", summary="This endpoint accepts text and returns audio file")
# async def speak_audio(request: Request, request_id:str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
async def get_audio_for_request(request: Request, request_id:str, db: Session = Depends(get_db)):
    try:
        object_name=f"{request_id}.wav"
        audio_data=read_object_from_minio(bucket_name='tts-audios', object_name=object_name)
        audio_stream = BytesIO(audio_data)
        return StreamingResponse(audio_stream, media_type="audio/wav", headers={"Content-Disposition": f"inline; filename={object_name}"})
    except Exception as e:
        logging.info(f"Error retrieving audio for request_id {request_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Audio not found for request_id: {request_id}")

