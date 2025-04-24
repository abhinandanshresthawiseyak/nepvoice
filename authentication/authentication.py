# import os
# from fastapi import FastAPI, Request
# from fastapi.responses import RedirectResponse, HTMLResponse
# from urllib.parse import urlencode
# import httpx
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # Environment variables
# CLIENT_ID = os.getenv("CLIENT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# REDIRECT_URI = os.getenv("REDIRECT_URI")
# AUTH_URI = os.getenv("AUTH_URI")
# TOKEN_URI = os.getenv("TOKEN_URI")
# USERINFO_URI = os.getenv("USERINFO_URI")

# # Create FastAPI app
# app = FastAPI()


# @app.get("/")
# async def index():
#     return HTMLResponse('<a href="/login">Login with Google</a>')


# @app.get("/login")
# async def login():
#     params = {
#         "client_id": CLIENT_ID,
#         "redirect_uri": REDIRECT_URI,
#         "response_type": "code",
#         "scope": "openid email profile",
#         "access_type": "offline",
#         "prompt": "consent"
#     }
#     url = f"{AUTH_URI}?{urlencode(params)}"
#     return RedirectResponse(url)


# @app.get("/auth/callback")
# async def auth_callback(request: Request):
#     code = request.query_params.get("code")
#     if not code:
#         return HTMLResponse("No authorization code provided.", status_code=400)

#     data = {
#         "code": code,
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "redirect_uri": REDIRECT_URI,
#         "grant_type": "authorization_code"
#     }

#     async with httpx.AsyncClient() as client:
#         token_resp = await client.post(TOKEN_URI, data=data)
#         token_data = token_resp.json()

#         if "access_token" not in token_data:
#             return HTMLResponse("Failed to retrieve access token.", status_code=400)

#         headers = {"Authorization": f"Bearer {token_data['access_token']}"}
#         userinfo_resp = await client.get(USERINFO_URI, headers=headers)
#         user_info = userinfo_resp.json()

#     return user_info



import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from urllib.parse import urlencode
import httpx
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, MetaData, Table
import databases

# Load .env
load_dotenv()

# OAuth Config
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
AUTH_URI = os.getenv("AUTH_URI")
TOKEN_URI = os.getenv("TOKEN_URI")
USERINFO_URI = os.getenv("USERINFO_URI")

# Database config
DATABASE_URL = os.getenv("DATABASE_URL")
database = databases.Database(DATABASE_URL)
metadata = MetaData()

# User table
users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),
    Column("email", String),
    Column("name", String),
    Column("picture", String),
)

# Create database engine and table
engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

# FastAPI app
app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def index():
    return HTMLResponse('<a href="/login">Login with Google</a>')


@app.get("/login")
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


# @app.get("/auth/callback")
# async def auth_callback(request: Request):
#     code = request.query_params.get("code")
#     if not code:
#         return HTMLResponse("No code provided", status_code=400)

#     data = {
#         "code": code,
#         "client_id": CLIENT_ID,
#         "client_secret": CLIENT_SECRET,
#         "redirect_uri": REDIRECT_URI,
#         "grant_type": "authorization_code"
#     }

#     async with httpx.AsyncClient() as client:
#         token_resp = await client.post(TOKEN_URI, data=data)
#         token_data = token_resp.json()

#         if "access_token" not in token_data:
#             return HTMLResponse("Failed to get token", status_code=400)

#         headers = {"Authorization": f"Bearer {token_data['access_token']}"}
#         userinfo_resp = await client.get(USERINFO_URI, headers=headers)
#         user_info = userinfo_resp.json()

#     # Save to DB
#     query = users.insert().values(
#         id=user_info.get("id"),
#         email=user_info.get("email"),
#         name=user_info.get("name"),
#         picture=user_info.get("picture")
#     )
#     await database.execute(query)

#     return HTMLResponse(f"<h3>Logged in as {user_info.get('name')}</h3><img src='{user_info.get('picture')}' width='100'/>")


from fastapi.responses import RedirectResponse

@app.get("/auth/callback")
async def auth_callback(request: Request):
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
    query = users.select().where(users.c.id == user_id)
    existing_user = await database.fetch_one(query)

    if existing_user:
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
    insert_query = users.insert().values(
        id=user_id,
        email=user_info.get("email"),
        name=user_info.get("name"),
        picture=user_info.get("picture")
    )
    await database.execute(insert_query)

    return HTMLResponse(
        content=f"""
            <h3>Welcome, {user_info.get("name")}!</h3>
            <img src="{user_info.get("picture")}" width="100">
            <p>You have successfully signed in.</p>
        """,
        status_code=200
    )
