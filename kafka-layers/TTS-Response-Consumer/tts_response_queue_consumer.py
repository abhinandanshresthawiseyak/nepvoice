from backend.app.utils.kafkaclient import KafkaClient
import time, json
from datetime import datetime
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    kafkaClient = KafkaClient(bootstrap_servers='192.168.88.40:19092')
    kafkaClient.initialize_consumer(group_id='tts-response-consumer-group')
    kafkaClient.consumer.subscribe(['tts_response_queue_topic'])
    
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
            
            data = msg.value()
            
            # 🔊 Save audio to file
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"/app/tts_audios/tts_audio_{timestamp}.mp3"  # or .wav depending on format
            with open(filename, "wb") as f:
                f.write(data)
            logger.info(f"✅ Saved audio to: {filename}")
            
        except Exception as e:
            logger.info(f"Error while polling messages: {e}")
            break
except Exception as e:
    logger.info(f"Consumer exception: {e}")
finally:
    kafkaClient.consumer.close()
    logger.info("Consumer closed.")