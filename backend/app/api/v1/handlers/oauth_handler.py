# # app/api/v1/handlers/oauth_handler.py

# import os
# import httpx
# from urllib.parse import urlencode
# from fastapi import Request, HTTPException
# from fastapi.responses import HTMLResponse, RedirectResponse
# from sqlalchemy import select, update, insert, func
# from database.database import database, users, user_credits

# CLIENT_ID = os.getenv("CLIENT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# REDIRECT_URI = os.getenv("REDIRECT_URI")
# AUTH_URI = os.getenv("AUTH_URI")
# TOKEN_URI = os.getenv("TOKEN_URI")
# USERINFO_URI = os.getenv("USERINFO_URI")

# def get_login_url():
#     params = {
#         "client_id": CLIENT_ID,
#         "redirect_uri": REDIRECT_URI,
#         "response_type": "code",
#         "scope": "openid email profile",
#         "access_type": "offline",
#         "prompt": "consent"
#     }
#     return f"{AUTH_URI}?{urlencode(params)}"

# async def handle_google_callback(request: Request):
#     if not database.is_connected:
#         await database.connect()

#     code = request.query_params.get("code")
#     if not code:
#         raise HTTPException(status_code=400, detail="No authorization code provided.")

#     async with httpx.AsyncClient() as client:
#         token_resp = await client.post(TOKEN_URI, data={
#             "code": code,
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET,
#             "redirect_uri": REDIRECT_URI,
#             "grant_type": "authorization_code"
#         })
#         token_data = token_resp.json()
#         access_token = token_data.get("access_token")
#         if not access_token:
#             raise HTTPException(status_code=400, detail="Failed to get access token.")

#         userinfo_resp = await client.get(USERINFO_URI, headers={"Authorization": f"Bearer {access_token}"})
#         user_info = userinfo_resp.json()

#     user_id = user_info.get("id")
#     email = user_info.get("email")
#     name = user_info.get("name")
#     picture = user_info.get("picture")

#     existing_user = await database.fetch_one(select(users).where(users.c.id == user_id))
#     if existing_user:
#         await database.execute(update(users).where(users.c.id == user_id).values(last_login_at=func.now()))
#         return HTMLResponse("<script>alert('Welcome back!'); window.location.href='/';</script>", status_code=200)

#     await database.execute(insert(users).values(id=user_id, email=email, name=name, picture=picture, last_login_at=func.now()))
#     await database.execute(insert(user_credits).values(user_id=user_id, credits_balance=0))

#     return HTMLResponse(f"""
#         <h3>Welcome, {name}!</h3>
#         <img src="{picture}" width="100">
#         <p>You have successfully signed in and a credit wallet has been created.</p>
#     """, status_code=200)

import os
import httpx
from urllib.parse import urlencode
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import SessionLocal
from app.models.models import User, UserCredit

from app.core import config

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


async def handle_callback(code):
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
        existing_user = db.query(User).filter(User.id == user_id).first()

        if existing_user:
            existing_user.last_login_at = func.now()
            db.commit()
            return name, "existing"

        # Create new user
        new_user = User(
            id=user_id,
            email=email,
            name=name,
            picture=picture,
            last_login_at=func.now()
        )
        db.add(new_user)
        db.commit()

        # Create credit wallet
        new_credit = UserCredit(
            user_id=user_id,
            credits_balance=0
        )
        db.add(new_credit)
        db.commit()

        return name, "new"
    finally:
        db.close()
