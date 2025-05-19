from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from app.api.v1.handlers import oauth_handler
from fastapi.middleware.cors import CORSMiddleware
from app.models.models import UserActivityLog
from app.database.database import SessionLocal
from sqlalchemy import func
from app.api.v1.handlers.session import get_logged_in_user

router = APIRouter()

@router.get("/")
async def index():
    return HTMLResponse('<a href="/auth/login">Login with Google</a>')

@router.get("/login")
async def login():
    url = oauth_handler.get_login_url()
    return RedirectResponse(url)

@router.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("No authorization code provided.", status_code=400)

    # Updated to return user_id instead of ssid
    session_id = request.cookies.get("session")  # The default name from SessionMiddleware
    name, user_id, status = await oauth_handler.handle_callback(code,session_id)

    if status == "Failed to get access token.":
        return HTMLResponse("Failed to get access token.", status_code=400)

    # Save user_id in session (this uses the session_id cookie under the hood)
    request.session["user_id"] = user_id

    # html = f"""
    # <!DOCTYPE html>
    # <html>
    #   <head><title>Logged In</title></head>
    #   <body>
    #     <h1>✅ Login Successful</h1>
    #     <p>Hi {name}, your session has been saved.</p>
    #     <p>You can now visit <a href='https://nepvoice.wiseyak.com/'>the app</a>.</p>
    #     <p>You can also visit <a href='http://localhost:8000/docs'>the docs</a>.</p>
    #   </body>
    # </html>
    # """
    # return HTMLResponse(content=html)
    return RedirectResponse(url="http://192.168.85.118:8005/app")

@router.post("/logout")
def logout_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = SessionLocal()
    try:
        session = db.query(UserActivityLog).filter(
            UserActivityLog.user_id == user_id,
            UserActivityLog.activity_type == "login",
            UserActivityLog.logged_out == None
        ).order_by(UserActivityLog.logged_in.desc()).first()

        if not session:
            raise HTTPException(status_code=404, detail="No active session found.")

        session.logged_out = func.now()
        db.commit()

        request.session.clear()  # Clear the session
        return {"message": "Logged out successfully"}
    finally:
        db.close()

@router.get("/whoami")
def whoami(request: Request):
    user = get_logged_in_user(request)
    return {
        "user_id": user.id,
        "name": user.name,
        "email": user.email,
        "picture": user.picture,
    }

