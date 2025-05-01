from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.api.v1.handlers.oauth_handler import get_login_url, handle_google_callback

router = APIRouter()

@router.get("/login/google")
async def login_via_google():
    """
    Redirect the user to Google's OAuth2 login page.
    """
    login_url = get_login_url()
    return RedirectResponse(login_url)

@router.get("/callback/google")
async def google_callback(request: Request):
    """
    Handle the Google OAuth2 callback.
    """
    return await handle_google_callback(request)
