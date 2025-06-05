# app/utils/api_key.py
import secrets

def generate_secure_api_key() -> str:
    return secrets.token_urlsafe(32)
