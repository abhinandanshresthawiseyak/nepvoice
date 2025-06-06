# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# COPY backend/app/utils/kafkaclient.py /app/backend/app/utils/kafkaclient.py
# COPY backend/app/api/v2/handlers/feature_asr_handler.py /app/backend/app/api/v2/handlers/feature_asr_handler.py
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY kafka-layers/ASR-Request-Consumer/asr_request_queue_consumer.py /app/asr_request_queue_consumer.py
CMD ["python", "asr_request_queue_consumer.py"]
