import requests, io
from app.utils.minio_utils import read_object_from_minio

def send_audio(url: str, bucket_name: str, object_name:str) -> dict:
    headers = {
        'accept': 'application/json',
    }

    audio_bytes = read_object_from_minio(bucket_name=bucket_name, object_name=object_name)
    
    # Set a filename and content type for the multipart/form-data
    file = {
        'audio': ('audio.wav', io.BytesIO(audio_bytes), 'audio/wav')
    }

    response = requests.post(
        url,
        headers=headers,
        files=file
    )

    # Return the response as JSON
    return response.json()