import os
import httpx
from urllib.parse import urlencode
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import SessionLocal
from app.models.models import User, UserCredit, UserActivityLog

from app.core import config
import random

CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET
REDIRECT_URI = config.REDIRECT_URI
AUTH_URI = config.AUTH_URI
TOKEN_URI = config.TOKEN_URI
USERINFO_URI = config.USERINFO_URI


def get_login_url():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{AUTH_URI}?{urlencode(params)}"

# def generate_ssid():
#     return random.randint(100000, 999999)

async def handle_callback(code,session_id):
    # Exchange authorization code for access token
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(TOKEN_URI, data=data)
        token_data = token_resp.json()

        if "access_token" not in token_data:
            return None, "Failed to get access token."

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        userinfo_resp = await client.get(USERINFO_URI, headers=headers)
        user_info = userinfo_resp.json()

    user_id = user_info.get("id")
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    db: Session = SessionLocal()
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.id == user_id).first()
        if existing_user:
            existing_user.last_login_at = func.now()
            db.commit()
            user = existing_user
        else:
            # Create new user
            user = User(
                id=user_id,
                email=email,
                name=name,
                picture=picture,
                role_level=1,
                last_login_at=func.now()
            )
            db.add(user)
            db.commit()

            # ✅ Create credit wallet (important!)
            new_credit = UserCredit(
                user_id=user_id,
                credits_balance=0
            )
            db.add(new_credit)
            db.commit()

        # Create login session
        # ssid = generate_ssid()
        activity_log = UserActivityLog(
            user_id=user_id,
            activity_type="login",
            ssid=session_id,
            logged_in=func.now(),
            ip_address="",  # you can pass this from request
            user_agent=""    # you can pass this from request
        )
        db.add(activity_log)
        db.commit()
        # return user.name, ssid, "existing" if existing_user else "new"
        return user.name,user.id, "existing" if existing_user else "new"
    finally:
        db.close()
