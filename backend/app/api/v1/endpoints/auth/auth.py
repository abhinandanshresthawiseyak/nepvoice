import os
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from urllib.parse import urlencode
import httpx
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.core.config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, AUTH_URI, TOKEN_URI, USERINFO_URI

router = APIRouter()

@router.get("/")
async def index():
    return HTMLResponse('<a href="/login">Login with Google</a>')

@router.get("/login")
async def login():
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{AUTH_URI}?{urlencode(params)}"
    return RedirectResponse(url)

@router.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("No authorization code provided.", status_code=400)

    # Exchange code for access token
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
            return HTMLResponse("Failed to get token", status_code=400)

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        userinfo_resp = await client.get(USERINFO_URI, headers=headers)
        user_info = userinfo_resp.json()

    user_id = user_info.get("id")

    # Check if user already exists
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user:
        # Already signed in, redirect with message
        return HTMLResponse(
            content=f"""
                <script>
                    alert("This account is already signed in!");
                    window.location.href = "/";
                </script>
            """,
            status_code=200
        )

    # Insert new user
    new_user = User(
        id=user_id,
        email=user_info.get("email"),
        name=user_info.get("name"),
        picture=user_info.get("picture")
    )
    db.add(new_user)
    db.commit()

    return HTMLResponse(
        content=f"""
            <h3>Welcome, {user_info.get("name")}!</h3>
            <img src="{user_info.get("picture")}" width="100">
            <p>You have successfully signed in.</p>
        """,
        status_code=200
    )
