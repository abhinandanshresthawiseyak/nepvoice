from backend.app.utils.kafkaclient import KafkaClient
import time, json
from datetime import datetime
import logging
import pusher
import base64, os
from dotenv import load_dotenv

load_dotenv()

KAFKA_SERVER = os.getenv("KAFKA_SERVER")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    pusher_client = pusher.Pusher(
        app_id='1999579',
        key='043a1db401ff46a9467c',
        secret='d567dae60b444305e93e',
        cluster='ap2',
        ssl=True
    )
    
    kafkaClient = KafkaClient(bootstrap_servers=KAFKA_SERVER)
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
            
            channel_id=msg.key().decode('utf-8')
            logger.info(f"Received message for channel: {channel_id}")
            data = json.loads(msg.value().decode('utf-8'))
            logger.info(f"Data received: {len(data['object_name'])} bytes for request_id {data['request_id']}")
            # pusher_client.trigger(channel_id, 'my-event', data)

        except Exception as e:
            logger.info(f"Error while polling messages: {e}")
            break
except Exception as e:
    logger.info(f"Consumer exception: {e}")
finally:
    kafkaClient.consumer.close()
    logger.info("Consumer closed.")