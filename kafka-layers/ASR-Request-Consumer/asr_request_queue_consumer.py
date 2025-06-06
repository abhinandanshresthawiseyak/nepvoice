from backend.app.api.v2.handlers.feature_asr_handler import send_audio
from backend.app.api.v2.handlers.features_handler import handle_feature_use
from backend.app.utils.kafkaclient import KafkaClient
from backend.app.utils.minio_utils import upload_audio_to_minio
import time, json, base64, logging, os, io
from datetime import datetime
from dotenv import load_dotenv
from backend.app.database.database import get_db

load_dotenv()

KAFKA_SERVER = os.getenv("KAFKA_SERVER")
asr_OBJECT_PREFIX = os.getenv("ASR_OBJECT_PREFIX")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    db=get_db()
    
    kafkaClient = KafkaClient(bootstrap_servers=KAFKA_SERVER)
    kafkaClient.initialize_consumer(group_id='asr-consumer-group')
    kafkaClient.consumer.subscribe(['asr_request_queue_topic'])
    
    kafkaClient.initialize_producer()
    
    logger.info("🔄 Listening for messages...")
    while True:
        try:
            # logger.info(f"Running {running_asr} asr tasks")
            # Check kafka connection periodically maybe every 10 seconds
            if time.time() % 10 < 1:
                logger.info("Checking Kafka connection...")
                kafkaClient.check_kafka_connection()
            
            msg = kafkaClient.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                logger.info(f"Error: {msg.error()}")
                continue
            
            data = json.loads(msg.value().decode('utf-8'))
            
            # Step1: Consume whole message
            object_name=data['object_name'] 
            bucket_name=data['bucket_name']   
            lang=data['lang']  
            user_id=data['user_id']  
            ip_address=data['ip_address']  
            user_agent=data['user_agent']  
            session_id=data['session_id']
            
            # Step2: Handle feature use
            result, error = handle_feature_use(
                user_id=user_id,
                feature_name="speech_to_text",  # your feature name in DB
                ip_address=ip_address,
                user_agent=user_agent,
                session_id=session_id
            )
            if error:
                if error == "Feature not found.":
                    raise HTTPException(status_code=404, detail=error)
                elif error == "User wallet not found.":
                    raise HTTPException(status_code=404, detail=error)
                elif error == "Insufficient credits.":
                    raise HTTPException(status_code=402, detail=error)
                else:
                    raise HTTPException(status_code=400, detail=error)
            
            # print(audio_name)
            # Step 3: Get Transcript
            if lang == 'english':
                transcript = send_audio(url=ASR_ENGLISH, object_name=object_name, bucket_name=bucket_name)
            elif lang == 'nepali':
                transcript = send_audio(url=ASR_NEPALI, object_name=object_name, bucket_name=bucket_name)
            else:
                raise ValueError("Invalid language selected. Only 'english' or 'nepali' are supported.")
            
            transcript_text = transcript.strip()
            
            # Step 4: Store ASRHistory
            asr_record = ASRHistory(
                user_id=data['user_id'] if data['user_id'] else None,
                language=lang,
                transcript=transcript_text,
                bucket_name=bucket_name,
                object_name=object_name
            )
            db.add(asr_record)
            db.commit()
            db.refresh(asr_record)

            # Step 5: Store transcript as .txt file so that frontend can access the text
            transcript_bytes = transcript_text.encode("utf-8")
            bucket_name, object_name= upload_audio_to_minio(audio_bytes=io.BytesIO(transcript_bytes), bucket_name=MINIO_BUCKET, object_name=f"{ASR_OBJECT_PREFIX}/{data['request_id']}.txt")
            
            kafkaClient.producer.produce('asr_response_queue_topic', key=data['request_id'], value=json.dumps({'request_id':data['request_id'],'bucket_name':bucket_name ,'object_name':object_name, 'text':data['text'], 'language':data['lang'], 'audio_size':len(audio_bytes), 'created_at': str(datetime.now())}), callback=kafkaClient.delivery_report)
            logger.info(f"Produced message at key {data['request_id']}")
        except Exception as e:
            logger.info(f"Error while polling messages: {e}")
            break
except Exception as e:
    logger.info(f"Consumer exception: {e}")
finally:
    kafkaClient.consumer.close()
    logger.info("Consumer closed.")