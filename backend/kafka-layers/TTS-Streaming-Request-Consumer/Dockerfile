# Dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
        ffmpeg 

# COPY backend/app/utils/kafkaclient.py /app/backend/app/utils/kafkaclient.py
# COPY backend/app/api/v2/handlers/feature_tts_handler.py /app/backend/app/api/v2/handlers/feature_tts_handler.py
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY kafka-layers/TTS-Streaming-Request-Consumer/tts_streaming_request_queue_consumer.py /app/backend/tts_streaming_request_queue_consumer.py
WORKDIR /app/backend
CMD ["python", "tts_streaming_request_queue_consumer.py"]
