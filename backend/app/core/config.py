from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

<<<<<<< HEAD
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_URI = os.getenv("AUTH_URI")
TOKEN_URI = os.getenv("TOKEN_URI")
USERINFO_URI = os.getenv("USERINFO_URI")

SECRET_KEY=os.getenv("SECRET_KEY")
=======
CLIENT_ID = "1039402342826-4dcealkuk6osr3qjdirmmetqkk4n4a1p.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://localhost:8000/auth/callback"
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
USERINFO_URI = "https://www.googleapis.com/oauth2/v2/userinfo"

# REDIRECT_URI = "https://aa90-113-199-192-49.ngrok-free.app/auth/callback"
>>>>>>> ce79d2ddd3f8066555e5a78e0bdb97148f10c909
