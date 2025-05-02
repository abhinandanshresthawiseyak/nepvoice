from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.api.v1.handlers import oauth_handler

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

    name, status = await oauth_handler.handle_callback(code)

    if status == "Failed to get access token.":
        return HTMLResponse("Failed to get access token.", status_code=400)

    if status == "existing":
        return HTMLResponse(
            content="""
                <script>
                    alert("Welcome back!");
                    window.location.href = "/";
                </script>
            """,
            status_code=200
        )

    return HTMLResponse(
        content=f"""
            <h3>Welcome, {name}!</h3>
            <p>You have successfully signed in and a credit wallet has been created.</p>
        """,
        status_code=200
    )
