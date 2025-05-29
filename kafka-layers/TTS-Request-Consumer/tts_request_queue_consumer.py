from backend.app.api.v2.handlers.feature_tts_handler import generate_tts_audio
from backend.app.utils.kafkaclient import KafkaClient
import time, json
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    kafkaClient = KafkaClient(bootstrap_servers='192.168.88.40:19092')
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
            logger.info(f"Audio length: {len(audio_bytes)}, Type: {type(audio_bytes)}")
            kafkaClient.producer.produce('tts_response_queue_topic', key=data['request_id']+str(data['text']), value=audio_bytes, callback=kafkaClient.delivery_report)
            logger.info(f"Produced message at key {data['request_id']}")
        except Exception as e:
            logger.info(f"Error while polling messages: {e}")
            break
except Exception as e:
    logger.info(f"Consumer exception: {e}")
finally:
    kafkaClient.consumer.close()
    logger.info("Consumer closed.")