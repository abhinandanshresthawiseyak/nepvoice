from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

PRODUCTION=False

if PRODUCTION:
    REDIRECT_URI= os.getenv("REDIRECT_URI_PROD")
    frontend_url = os.getenv("FRONTEND_URL_PROD")
else:
    REDIRECT_URI= os.getenv("REDIRECT_URI")
    frontend_url = os.getenv("FRONTEND_URL")

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_URI = os.getenv("AUTH_URI")
TOKEN_URI = os.getenv("TOKEN_URI")
USERINFO_URI = os.getenv("USERINFO_URI")

SECRET_KEY=os.getenv("SECRET_KEY")



# ✅ Get allowed origins as a list
raw_origins = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]