from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from app.api.v1.handlers import oauth_handler
from fastapi.middleware.cors import CORSMiddleware
from app.models.models import UserActivityLog
from app.database.database import SessionLocal
from sqlalchemy import func

router = APIRouter()



@router.get("/")
async def index():
    return HTMLResponse('<a href="/auth/login">Login with Google</a>')


@router.get("/login")
async def login():
    url = oauth_handler.get_login_url()
    return RedirectResponse(url)


# @router.get("/callback")
# async def auth_callback(request: Request):
#     code = request.query_params.get("code")
#     if not code:
#         return HTMLResponse("No authorization code provided.", status_code=400)

#     name, status = await oauth_handler.handle_callback(code)

#     if status == "Failed to get access token.":
#         return HTMLResponse("Failed to get access token.", status_code=400)

#     if status == "existing":
#         return HTMLResponse(
#             content="""
#                 <script>
#                     alert("Welcome back!");
#                     window.location.href = "/";
#                 </script>
#             """,
#             status_code=200
#         )

#     return HTMLResponse(
#         content=f"""
#             <h3>Welcome, {name}!</h3>
#             <p>You have successfully signed in and a credit wallet has been created.</p>
#         """,
#         status_code=200
#     )


from fastapi.responses import RedirectResponse

@router.get("/callback")
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("No authorization code provided.", status_code=400)

    name, ssid, status = await oauth_handler.handle_callback(code)


    if status == "Failed to get access token.":
        return HTMLResponse("Failed to get access token.", status_code=400)

    # ✅ Always redirect after login (whether new or existing user)
    redirect_url = "https://nepvoice.wiseyak.com/app"  # Replace with your actual redirect URL

    return RedirectResponse(url=redirect_url)



@router.post("/logout")
def logout_user(user_id: str = Query(...)):
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
        return {"message": f"User {user_id} logged out successfully.", "ssid": session.ssid}
    finally:
        db.close()