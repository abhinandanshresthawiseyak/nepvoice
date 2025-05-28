from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.database.database import init_db
from app.api.v1.endpoints import oauth, credit, features, admin
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import SECRET_KEY
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1.endpoints.feature import chatbot, callbot, asr, tts
from fastapi.staticfiles import StaticFiles  # ✅ Add this
from app.core.config import ALLOWED_ORIGINS
#("ALLOWED_ORIGINS").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]  
from app.core.config import PRODUCTION

app = FastAPI()

app.add_middleware(CORSMiddleware,
                allow_origins=ALLOWED_ORIGINS,
                   allow_credentials=True,
                   allow_methods=["*"], # Allows all HTTP methods
                   allow_headers=["*"])

# app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

if PRODUCTION:
    app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session_login",              # Optional: default name
    same_site="none",                      # Required for cross-site
    https_only=True,                       # Required for SameSite=None
    domain=".wiseyak.com")   
                   # ✅ Enables subdomain sharing
else:
    # app.add_middleware(
    #     SessionMiddleware,
    #     secret_key=SECRET_KEY,
    #     session_cookie="session_login",
    #     same_site="lax",       # ← change from "none" to "lax"
    #     https_only=False,      # ← must be False for HTTP
    #     domain=None,           # ← don't set domain unless using subdomains
    # )
    # """the above code is for local development"""
        app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session_login",              # Optional: default name
    same_site="none",                      # Required for cross-site
    https_only=True,                       # Required for SameSite=None
    domain=".wiseyak.com")   
        


@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
async def root():
    return HTMLResponse('<a href="/auth/login">Login with Google</a>')

# Include routers
app.include_router(oauth.router, prefix="/auth")
app.include_router(credit.router, prefix="/credits")
app.include_router(features.router, prefix="")
app.include_router(admin.router, prefix="")
app.include_router(chatbot.router, prefix="/feature/chatbot")
app.include_router(callbot.router, prefix="/feature/callbot")
app.include_router(asr.router, prefix="/feature/asr")
app.include_router(tts.router, prefix="/feature/tts")

