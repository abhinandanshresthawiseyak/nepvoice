from app.api.v2.handlers.feature_tts_handler import generate_tts_audio
from app.utils.kafkaclient import KafkaClient
from app.utils.minio_utils import upload_audio_to_minio
import time, json, base64, logging
from datetime import datetime
from dotenv import load_dotenv
import os, requests
from io import BytesIO
from pydub import AudioSegment
# from datetime import datetime
# from urlextract import URLExtract

load_dotenv()

# Load environment variables
TTS_URI=os.getenv('TTS')
TTS_FILE_LOCATION=os.getenv('TTS_FILE_LOCATION')
TTS_API_KEY=os.getenv('TTS_API_KEY')
KAFKA_SERVER=os.getenv('KAFKA_SERVER')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_tts_audio(text: str, language: str):
    """
    Helper function to generate TTS audio for the given text and language.
    """
    query_params = {
        "audio_flag": "true",
        "is_container": "false"
    }
    
    payload = {"text": text, 
               "language": language}

    
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        "x-api-key": TTS_API_KEY
    }

    try:
        # print(TTS_URI, query_params, payload, headers)
        response = requests.post(TTS_URI, params=query_params, data=payload, headers=headers)
        response.raise_for_status()
        return response.content  # Return the audio content directly
        # audio_filename = f"{uuid.uuid4()}.wav"
        # audio_file_path = os.path.join(TTS_FILE_LOCATION, audio_filename)
        # with open(audio_file_path, "wb") as audio_file:
        #     audio_file.write(response.content)
        # return audio_file_path
    except requests.exceptions.Timeout:
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")

try:
    kafkaClient = KafkaClient(bootstrap_servers=KAFKA_SERVER)
    kafkaClient.initialize_consumer(group_id='tts-consumer-group')
    kafkaClient.consumer.subscribe(['tts_streaming_request_queue_topic'])
    
    kafkaClient.initialize_producer()
    audio_bytes = None
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
            
            audio_bytes = generate_tts_audio(text=data['text'], language=data['lang'])
            wav_bytes = BytesIO(audio_bytes)
            print("got wav bytes of length: ", len(wav_bytes.getvalue()))
            audio_segment = AudioSegment.from_file(wav_bytes, format="wav")

            # 3. Export the AudioSegment to MP3 in-memory.
            mp3_buffer = BytesIO()
            audio_segment.export(mp3_buffer, format="mp3")
            mp3_bytes = mp3_buffer.getvalue()
            # if data['text'] == 'EndOfStream':
            #     kafkaClient.producer.produce('tts_streaming_response_queue_topic', key=data['request_id']+'EndOfStream', value=audio_bytes, callback=kafkaClient.delivery_report)
            # else:
            #     kafkaClient.producer.produce('tts_streaming_response_queue_topic', key=data['request_id'], value=audio_bytes, callback=kafkaClient.delivery_report)
            if data['text'] == 'EndOfStream':
                kafkaClient.producer.produce('tts_streaming_response_queue_topic', key=data['request_id']+'EndOfStream', value=mp3_bytes, callback=kafkaClient.delivery_report)
            else:
                kafkaClient.producer.produce('tts_streaming_response_queue_topic', key=data['request_id'], value=mp3_bytes, callback=kafkaClient.delivery_report)
            
            logger.info(f"Produced message at key {data['request_id']}")
            
        except Exception as e:
            logger.info(f"Error while polling messages: {e}")
            break
except Exception as e:
    logger.info(f"Consumer exception: {e}")
finally:
    kafkaClient.consumer.close()
    logger.info("Consumer closed.")