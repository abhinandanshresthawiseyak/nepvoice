# app/api/v1/handlers/oauth_handler.py

import os
import httpx
from urllib.parse import urlencode
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, update, insert, func
from database.database import database, users, user_credits

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_URI = os.getenv("AUTH_URI")
TOKEN_URI = os.getenv("TOKEN_URI")
USERINFO_URI = os.getenv("USERINFO_URI")

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

async def handle_google_callback(request: Request):
    if not database.is_connected:
        await database.connect()

    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="No authorization code provided.")

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(TOKEN_URI, data={
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code"
        })
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token.")

        userinfo_resp = await client.get(USERINFO_URI, headers={"Authorization": f"Bearer {access_token}"})
        user_info = userinfo_resp.json()

    user_id = user_info.get("id")
    email = user_info.get("email")
    name = user_info.get("name")
    picture = user_info.get("picture")

    existing_user = await database.fetch_one(select(users).where(users.c.id == user_id))
    if existing_user:
        await database.execute(update(users).where(users.c.id == user_id).values(last_login_at=func.now()))
        return HTMLResponse("<script>alert('Welcome back!'); window.location.href='/';</script>", status_code=200)

    await database.execute(insert(users).values(id=user_id, email=email, name=name, picture=picture, last_login_at=func.now()))
    await database.execute(insert(user_credits).values(user_id=user_id, credits_balance=0))

    return HTMLResponse(f"""
        <h3>Welcome, {name}!</h3>
        <img src="{picture}" width="100">
        <p>You have successfully signed in and a credit wallet has been created.</p>
    """, status_code=200)
