from backend.app.api.v2.handlers.feature_tts_handler import generate_tts_audio
from backend.app.utils.kafkaclient import KafkaClient
from backend.app.utils.minio_utils import upload_audio_to_minio
import time, json, base64, logging, os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

KAFKA_SERVER = os.getenv("KAFKA_SERVER")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    kafkaClient = KafkaClient(bootstrap_servers=KAFKA_SERVER)
    kafkaClient.initialize_consumer(group_id='tts-consumer-group')
    kafkaClient.consumer.subscribe(['tts_request_queue_topic'])
    
    kafkaClient.initialize_producer()
    
    logger.info("🔄 Listening for messages...")
    while True:
        try:
            # logger.info(f"Running {running_tts} TTS tasks")
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
            # logger.info(data)
            audio_bytes=generate_tts_audio(text=data['text'], language=data['lang'])
            object_name=upload_audio_to_minio(bucket_name='tts-audios', object_name=f"{data['request_id']}.wav", audio_bytes=audio_bytes, content_type='audio/wav')
            if object_name is None:
                logger.info("Failed to upload audio to MinIO")
                continue
            logger.info(f"Audio length: {len(audio_bytes)}, Type: {type(audio_bytes)}, Object Name: {object_name}")
            kafkaClient.producer.produce('tts_response_queue_topic', key=data['request_id'], value=json.dumps({'request_id':data['request_id'],'bucket_name':'tts-audios' ,'object_name':object_name, 'text':data['text'], 'language':data['lang'], 'audio_size':len(audio_bytes), 'created_at': str(datetime.now())}), callback=kafkaClient.delivery_report)
            logger.info(f"Produced message at key {data['request_id']}")
        except Exception as e:
            logger.info(f"Error while polling messages: {e}")
            break
except Exception as e:
    logger.info(f"Consumer exception: {e}")
finally:
    kafkaClient.consumer.close()
    logger.info("Consumer closed.")