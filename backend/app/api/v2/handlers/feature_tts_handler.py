
import os, re, uuid, requests, logging, asyncio
from fastapi import HTTPException
from dotenv import load_dotenv
from datetime import datetime
from urlextract import URLExtract
from io import BytesIO
from pydub import AudioSegment
from app.utils.minio_utils import upload_audio_to_minio
from app.utils.kafkaclient import KafkaClient

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
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
        # logging.info(TTS_URI, query_params, payload, headers)
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
    
async def audio_chunk_generator(request_id: str, kafkaClient):
    streamed_bytes = b''  # Initialize an empty bytes object to store streamed audio
    try:
        while True:
            msg = kafkaClient.consumer.poll(1.0)
            # logging.info(msg)
            if msg is None or msg.error():
                await asyncio.sleep(0.01)
                continue

            key = msg.key().decode('utf-8')
            if request_id not in key:
                # logging.info("Skipping message with key: %s, does not match request_id: %s", key, request_id)
                await asyncio.sleep(0.01)  # Avoid busy waiting
                continue

            if request_id in key and 'EndOfStream' in key:
                logging.info("End of stream reached for %s",request_id)
                break
            
            value = msg.value()
            logging.info("yielding audio chunk of length %s for request_id: %s", len(value),request_id)
            streamed_bytes += value  # Append the received bytes to the streamed_bytes
            # Yield the audio chunk
            yield value

    finally:
        # kafkaClient.consumer.close()
        if streamed_bytes:
            # Create an AudioSegment from the MP3 bytes
            audio = AudioSegment.from_mp3(BytesIO(streamed_bytes))
    
            wav_buffer = BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_buffer.seek(0)  # Rewind to start

            # Upload to MinIO
            object_name = f"{request_id}.wav"
            upload_result = upload_audio_to_minio(
                audio_bytes=wav_buffer.read(),
                bucket_name="tts-audios",
                object_name=object_name,
                content_type="audio/wav"
            )

            if upload_result:
                logging.info("Uploaded streamed audio to MinIO as %s", object_name)
            else:
                logging.info("Failed to upload streamed audio to MinIO")
    
class TTSPreprocessor:
    def preprocess_and_split_text(self, text, language):
        text=self.replace_dot_in_floating_numbers(text)
        text=self.check_links_in_str(text, language)
        text=self.transform_email(text)
        segments = self.split_text_naturally(text)
        return segments
    
    def split_into_chunks(self, strings, chunk_size=25):
            words = strings.split()
            
            result = []
            current_chunk = []

            current_length = 0
            for word in words:
                if current_length <= chunk_size:  
                    current_chunk.append(word)
                    current_length += 1  
                else:
                    # If adding the next word exceeds the chunk size, save the current chunk
                    result.append(' '.join(current_chunk))
                    # Start a new chunk with the current word
                    current_chunk = [word]
                    current_length = 1  # +1 for the space

            if current_chunk:
                result.append(' '.join(current_chunk))

            return result

    def merge_short_sentences(self, sentences, threshold=5):
        merged = []
        i = 0
        while i < len(sentences):
            current = sentences[i]
            if len(current.split()) < threshold and i + 1 < len(sentences):
                # Join current with the next one
                merged.append(current + " " + sentences[i + 1])
                i += 2  # Skip next one, since we merged it
            else:
                merged.append(current)
                i += 1
        return merged

    def replace_dot_in_floating_numbers(self,text):
        # Regex for both Latin and Devanagari decimal numbers
        pattern = r"(\d+\.\d+|[०-९]+\.[०-९]+)"
        decimal_numbers = re.findall(pattern, text)
        logging.info("Decimal numbers found: %s", decimal_numbers)

        for decimal_number in decimal_numbers:
            text=text.replace(decimal_number,decimal_number.replace('.',' point '))

        return text

    def remove_consecutive_duplicates(self, text):
        return re.sub(r'([,()\[\]\s]*in\s+provided\s+link)([,()\[\]\s]*\1)+', r'\1', text)

    def check_links_in_str(self, text, language):
        logging.info("language in str link: %s", language)
        text = text.replace('[', '').replace(']','').replace('(','').replace(')','')
        urls = URLExtract().find_urls(text, get_indices=True)

        for i, url in enumerate(urls):
            if i==0:
                if language == 'en':
                    text = text.replace(url[0], ' in provided link. ')
                else:
                    text = text.replace(url[0], ' प्रदान गरिएको लिंकमा ')
            else:
                if url[1][0] in range(urls[i-1][1][1], urls[i-1][1][1] + 4):
                    text = text.replace(url[0], '')

        text = self.remove_consecutive_duplicates(text)
        return text

    def transform_email(self,text):
        # Regex pattern to match email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

        # Function to replace '.' with ' dot ' and '@' with ' at '
        def replace_email(match):
            email = match.group(0)
            email = email.replace('.', ' dot ').replace('@', ' at ')
            return email

        # Use regex to find and replace the email
        return re.sub(email_pattern, replace_email, text)

    def split_text_naturally(self, text):
        text=text.strip('"')
        # logging.info("Split_tex_natural: ",type(text), text.strip('"'))
        # Split based on sentence-ending punctuation (e.g., '.', '!', '?') or line breaks
        split_text = text.split('\n')
        all_sentence = []

        for s_text in split_text:
            s_text=s_text.replace('\\n','')
            multi_split_sent = re.split(r'[\.?:]', s_text)
            cleaned_sentences = [sentence.strip() for sentence in multi_split_sent if sentence.strip()]
            no_symbols_only = [sentence for sentence in cleaned_sentences if not re.fullmatch(r'[\W_]+', sentence.strip())]

            all_sentence.extend([sentence.strip()+" , " for sentence in no_symbols_only if sentence.strip()])
        
        # logging.info(all_sentence)
        return all_sentence