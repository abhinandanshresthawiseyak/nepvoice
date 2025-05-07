POSTGRES_USER = "nepvoice"
POSTGRES_PASSWORD = "nepvoice"
POSTGRES_HOST = "192.168.88.40"
POSTGRES_PORT = "9090"
POSTGRES_DB = "nepvoice"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

CLIENT_ID = "1039402342826-4dcealkuk6osr3qjdirmmetqkk4n4a1p.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://192.168.88.40:8000/auth/callback"
AUTH_URI = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
USERINFO_URI = "https://www.googleapis.com/oauth2/v2/userinfo"

SECRET_KEY="asdfjiosajdfojsapdjfposiajdfoisadf"