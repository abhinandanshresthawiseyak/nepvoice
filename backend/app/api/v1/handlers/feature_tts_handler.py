
import os
import uuid
from fastapi import HTTPException
import requests

TTS_URI=os.getenv('TTS')
TTS_FILE_LOCATION=os.getenv('TTS_FILE_LOCATION')
TTS_API_KEY=os.getenv('TTS_API_KEY')

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
        response = requests.post(TTS_URI, params=query_params, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        audio_filename = f"{uuid.uuid4()}.wav"
        audio_file_path = os.path.join(TTS_FILE_LOCATION, audio_filename)
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(response.content)
        return audio_file_path
    except requests.exceptions.Timeout:
        audio_path_tts = "connection timeout"
        return audio_path_tts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the audio file. {e}")