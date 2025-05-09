import requests

def send_audio_file(url: str, audio_file_path: str) -> dict:
    headers = {
        'accept': 'application/json',
    }

    # Open the audio file and send a POST request
    with open(audio_file_path, 'rb') as audio_file:
        response = requests.post(
            url,
            headers=headers,
            files={'audio': audio_file}
        )

    # Return the response as JSON
    return response.json()